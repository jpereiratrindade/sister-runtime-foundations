#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <poll.h>
#include <sys/signalfd.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <charconv>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

static_assert(__cplusplus >= 202302L,
              "srf-runtime-probe requires the C++23 language mode");

class FileDescriptor {
 public:
  explicit FileDescriptor(const int value = -1) noexcept : value_(value) {}
  ~FileDescriptor() {
    if (value_ >= 0) {
      static_cast<void>(::close(value_));
    }
  }

  FileDescriptor(const FileDescriptor&) = delete;
  FileDescriptor& operator=(const FileDescriptor&) = delete;

  [[nodiscard]] int get() const noexcept { return value_; }

 private:
  int value_;
};

struct Options {
  std::filesystem::path file_path;
  std::uint16_t port = 0;
};

[[noreturn]] void fail(const std::string& message) {
  std::cerr << "error=" << message << '\n';
  std::exit(EXIT_FAILURE);
}

std::string sanitized(const char* value) {
  if (value == nullptr) {
    return "<unset>";
  }

  std::string result;
  for (const char raw_character : std::string_view(value)) {
    const auto character = static_cast<unsigned char>(raw_character);
    if (character >= 0x20U && character != 0x7FU && character != '=') {
      result.push_back(static_cast<char>(character));
    } else {
      result.push_back('?');
    }
  }
  return result;
}

std::uint16_t parse_port(const std::string_view raw) {
  unsigned int value = 0;
  const auto [end, error] =
      std::from_chars(raw.data(), raw.data() + raw.size(), value);
  if (error != std::errc{} || end != raw.data() + raw.size() ||
      value > std::numeric_limits<std::uint16_t>::max()) {
    fail("invalid --port value");
  }
  return static_cast<std::uint16_t>(value);
}

Options parse_options(const int argc, char* argv[]) {
  Options options;
  for (int index = 1; index < argc; ++index) {
    const std::string_view argument(argv[index]);
    if (argument == "--help") {
      std::cout << "Usage: srf-runtime-probe --file PATH [--port PORT]\n"
                   "Opens PATH and listens on 127.0.0.1; PORT 0 asks Linux "
                   "to select a port.\n";
      std::exit(EXIT_SUCCESS);
    }
    if (argument == "--file" && index + 1 < argc) {
      options.file_path = argv[++index];
      continue;
    }
    if (argument == "--port" && index + 1 < argc) {
      options.port = parse_port(argv[++index]);
      continue;
    }
    fail("unknown or incomplete argument");
  }

  if (options.file_path.empty()) {
    fail("--file PATH is required");
  }
  return options;
}

sigset_t blocked_shutdown_signals() {
  sigset_t signals;
  if (::sigemptyset(&signals) != 0 || ::sigaddset(&signals, SIGINT) != 0 ||
      ::sigaddset(&signals, SIGTERM) != 0 ||
      ::sigprocmask(SIG_BLOCK, &signals, nullptr) != 0) {
    fail(std::string("block shutdown signals: ") + std::strerror(errno));
  }
  return signals;
}

std::vector<int> open_file_descriptors() {
  long limit = ::sysconf(_SC_OPEN_MAX);
  if (limit < 0 || limit > 4096) {
    limit = 4096;
  }

  std::vector<int> result;
  for (int descriptor = 0; descriptor < static_cast<int>(limit); ++descriptor) {
    errno = 0;
    if (::fcntl(descriptor, F_GETFD) != -1 || errno != EBADF) {
      result.push_back(descriptor);
    }
  }
  return result;
}

void print_file_descriptors() {
  const auto descriptors = open_file_descriptors();
  std::cout << "open_fds=";
  for (std::size_t index = 0; index < descriptors.size(); ++index) {
    if (index != 0U) {
      std::cout << ',';
    }
    std::cout << descriptors[index];
  }
  std::cout << '\n';
}

}  // namespace

int main(const int argc, char* argv[]) {
  const Options options = parse_options(argc, argv);
  const sigset_t signals = blocked_shutdown_signals();
  FileDescriptor signal_events(
      ::signalfd(-1, &signals, SFD_CLOEXEC | SFD_NONBLOCK));
  if (signal_events.get() < 0) {
    fail(std::string("signalfd: ") + std::strerror(errno));
  }

  const std::string file_path = std::filesystem::absolute(options.file_path).string();
  FileDescriptor regular_file(
      ::open(file_path.c_str(), O_CREAT | O_RDWR | O_CLOEXEC, 0600));
  if (regular_file.get() < 0) {
    fail(std::string("open regular file: ") + std::strerror(errno));
  }

  constexpr std::string_view marker = "srf-runtime-probe regular file\n";
  const ssize_t written = ::write(regular_file.get(), marker.data(), marker.size());
  if (written < 0 || static_cast<std::size_t>(written) != marker.size()) {
    fail(std::string("write regular file: ") + std::strerror(errno));
  }

  FileDescriptor listener(::socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0));
  if (listener.get() < 0) {
    fail(std::string("socket: ") + std::strerror(errno));
  }

  const int reuse_address = 1;
  if (::setsockopt(listener.get(), SOL_SOCKET, SO_REUSEADDR, &reuse_address,
                   sizeof(reuse_address)) != 0) {
    fail(std::string("setsockopt: ") + std::strerror(errno));
  }

  sockaddr_in address{};
  address.sin_family = AF_INET;
  address.sin_port = htons(options.port);
  address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
  if (::bind(listener.get(), reinterpret_cast<const sockaddr*>(&address),
             sizeof(address)) != 0) {
    fail(std::string("bind: ") + std::strerror(errno));
  }
  if (::listen(listener.get(), 8) != 0) {
    fail(std::string("listen: ") + std::strerror(errno));
  }

  socklen_t address_size = sizeof(address);
  if (::getsockname(listener.get(), reinterpret_cast<sockaddr*>(&address),
                    &address_size) != 0) {
    fail(std::string("getsockname: ") + std::strerror(errno));
  }

  std::cout << "probe=srf-runtime-probe\n";
  std::cout << "cplusplus=" << __cplusplus << '\n';
  std::cout << "pid=" << ::getpid() << '\n';
  std::cout << "ppid=" << ::getppid() << '\n';
  std::cout << "uid=" << ::getuid() << '\n';
  std::cout << "gid=" << ::getgid() << '\n';
  std::cout << "cwd=" << std::filesystem::current_path().string() << '\n';
  std::cout << "environment.SRF_PROBE_CONTEXT="
            << sanitized(std::getenv("SRF_PROBE_CONTEXT")) << '\n';
  std::cout << "regular_file=" << file_path << '\n';
  std::cout << "regular_fd=" << regular_file.get() << '\n';
  std::cout << "listen_address=127.0.0.1\n";
  std::cout << "listen_port=" << ntohs(address.sin_port) << '\n';
  std::cout << "socket_fd=" << listener.get() << '\n';
  std::cout << "signal_wait=signalfd\n";
  std::cout << "signal_fd=" << signal_events.get() << '\n';
  print_file_descriptors();
  std::cout << "ready=1\n" << std::flush;

  int requested_shutdown_signal = 0;
  while (requested_shutdown_signal == 0) {
    pollfd descriptors[] = {
        {listener.get(), POLLIN, 0},
        {signal_events.get(), POLLIN, 0},
    };
    const int result = ::poll(descriptors, 2, -1);
    if (result < 0) {
      if (errno == EINTR) {
        continue;
      }
      fail(std::string("poll: ") + std::strerror(errno));
    }
    if ((descriptors[0].revents & POLLIN) != 0) {
      FileDescriptor connection(::accept4(listener.get(), nullptr, nullptr, SOCK_CLOEXEC));
      if (connection.get() < 0 && errno != EINTR) {
        fail(std::string("accept4: ") + std::strerror(errno));
      }
    }
    if ((descriptors[1].revents & POLLIN) != 0) {
      signalfd_siginfo signal_information{};
      const ssize_t bytes_read =
          ::read(signal_events.get(), &signal_information, sizeof(signal_information));
      if (bytes_read < 0) {
        if (errno == EAGAIN || errno == EINTR) {
          continue;
        }
        fail(std::string("read signalfd: ") + std::strerror(errno));
      }
      if (static_cast<std::size_t>(bytes_read) != sizeof(signal_information)) {
        fail("short read from signalfd");
      }
      const auto signal_number = static_cast<int>(signal_information.ssi_signo);
      if (signal_number != SIGINT && signal_number != SIGTERM) {
        fail("unexpected signal read from signalfd");
      }
      requested_shutdown_signal = signal_number;
    }
  }

  std::cout << "shutdown_signal=" << requested_shutdown_signal << '\n';
  std::cout << "shutdown=controlled\n" << std::flush;
  return EXIT_SUCCESS;
}
