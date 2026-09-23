import resource

CPU_SECONDS = 5
MEMORY_BYTES = 256 * 1024 * 1024
FILE_SIZE_BYTES = 8 * 1024 * 1024
MAX_PROCESSES = 64


def make_limiter(address_space=MEMORY_BYTES):
    def limit_resources():
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
        if address_space is not None:
            resource.setrlimit(resource.RLIMIT_AS, (address_space, address_space))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE_BYTES, FILE_SIZE_BYTES))
        resource.setrlimit(resource.RLIMIT_NPROC, (MAX_PROCESSES, MAX_PROCESSES))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return limit_resources


limit_resources = make_limiter()
limit_resources_no_address_space = make_limiter(address_space=None)