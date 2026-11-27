"""Read the Windows system commit budget before starting a mapped PE package.

The system commit limit includes RAM and paging-file backing; it is NOT the
amount of free physical RAM. This is a snapshot, not a reservation.
"""

import ctypes as C
import sys

MIB = 1 << 20


class PerformanceInformation(C.Structure):
    """Windows psapi.h PERFORMANCE_INFORMATION; DWORD is always 32 bits."""

    _fields_ = [
        ("cb", C.c_uint32),
        ("CommitTotal", C.c_size_t),
        ("CommitLimit", C.c_size_t),
        ("CommitPeak", C.c_size_t),
        ("PhysicalTotal", C.c_size_t),
        ("PhysicalAvailable", C.c_size_t),
        ("SystemCache", C.c_size_t),
        ("KernelTotal", C.c_size_t),
        ("KernelPaged", C.c_size_t),
        ("KernelNonpaged", C.c_size_t),
        ("PageSize", C.c_size_t),
        ("HandleCount", C.c_uint32),
        ("ProcessCount", C.c_uint32),
        ("ThreadCount", C.c_uint32),
    ]


def snapshot_from_pages(limit_pages, used_pages, page_size):
    """Pure conversion of GetPerformanceInfo page counts; never wrap under pressure."""
    if not page_size or not limit_pages:
        raise ValueError("Windows reported an invalid commit page size or limit")
    limit_bytes = int(limit_pages) * int(page_size)
    used_bytes = int(used_pages) * int(page_size)
    free_bytes = max(limit_bytes - used_bytes, 0)
    return {"limit_mib": limit_bytes // MIB, "used_mib": used_bytes // MIB,
            "available_mib": free_bytes // MIB, "available_bytes": free_bytes}


def read_host_commit():
    """GetPerformanceInfo from System32 psapi.dll; never reads guest image bytes."""
    if sys.platform != "win32":
        raise OSError("Windows system commit information requires a Windows host")
    info = PerformanceInformation()
    info.cb = C.sizeof(PerformanceInformation)
    # Only the Windows system copy, never a DLL planted beside the package.
    psapi = C.WinDLL("psapi.dll", winmode=0x800, use_last_error=True)
    get_performance = psapi.GetPerformanceInfo
    get_performance.argtypes = [C.POINTER(PerformanceInformation), C.c_uint32]
    get_performance.restype = C.c_int
    if not get_performance(C.byref(info), info.cb):
        raise OSError(C.get_last_error(), "GetPerformanceInfo failed")
    return snapshot_from_pages(info.CommitLimit, info.CommitTotal, info.PageSize)


def require_commit_budget(minimum_mib, snapshot):
    """Reject a requested budget before any guest module is mapped or started."""
    if not isinstance(minimum_mib, int) or minimum_mib < 0 or minimum_mib > 1 << 20:
        raise ValueError("--min-commit-mib must be between 0 and 1048576")
    if snapshot["available_bytes"] < minimum_mib * MIB:
        raise ValueError(
            f"Windows system commit headroom {snapshot['available_mib']} MiB is below the "
            f"requested {minimum_mib} MiB. This is commit budget, not free RAM: "
            "close other processes or review the Windows paging-file size")
    return {"limit_mib": snapshot["limit_mib"], "used_mib": snapshot["used_mib"],
            "available_mib": snapshot["available_mib"], "minimum_mib": minimum_mib,
            "meets_minimum": True}
