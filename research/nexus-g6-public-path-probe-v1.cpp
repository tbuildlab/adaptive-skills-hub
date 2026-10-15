// Finite PUBLIC-only path diagnostic. No candidate/runtime/model dependencies.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cerrno>
#include <fstream>
#include <iostream>
#include <string>

static const std::string legacy_prompt = "Output only PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE.\n/no_think\n";
static const std::string model_prompt = "<|im_start|>user\nOutput only PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE.\n/no_think<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n";
static const std::string prompt = model_prompt + "\n";
static std::string utf8(const std::wstring & value) {
    int size = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, value.data(),
                                  static_cast<int>(value.size()), nullptr, 0, nullptr, nullptr);
    if (size <= 0) return {};
    std::string out(size, '\0');
    WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()),
                        out.data(), size, nullptr, nullptr);
    return out;
}
static bool wide_read(const std::wstring & path, const std::string & expected) {
    HANDLE file = CreateFileW(path.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return false;
    char data[256]; DWORD size = 0;
    bool ok = ReadFile(file, data, sizeof(data), &size, nullptr) != 0;
    CloseHandle(file);
    return ok && std::string(data, size) == expected;
}
static bool narrow_read(const std::string & path, const std::string & expected, int * error = nullptr) {
    errno = 0;
    // Same narrow std::ifstream filename operation as the pinned -f parser.
    std::ifstream file(path);
    if (!file) { if (error) *error = errno; return false; }
    char data[256]; file.read(data, sizeof(data));
    return std::string(data, static_cast<size_t>(file.gcount())) == expected;
}
static bool denied_write(const std::wstring & path) {
    HANDLE file = CreateFileW(path.c_str(), GENERIC_WRITE, FILE_SHARE_READ, nullptr,
                              CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file == INVALID_HANDLE_VALUE) return true;
    CloseHandle(file); return false;
}
static void flag(const char * name, bool value) {
    std::cout << ",\"" << name << "\":" << (value ? "true" : "false");
}
static DWORD sentinel_path(HANDLE handle, wchar_t * buffer, DWORD size) {
    // Windows may raise STATUS_INVALID_HANDLE instead of returning an error for
    // an excluded handle. Match the existing public Python fixture's narrow
    // exception handling; never turn a different exception into a PASS.
    __try { return GetFinalPathNameByHandleW(handle, buffer, size, FILE_NAME_NORMALIZED); }
    __except(GetExceptionCode() == 0xc0000008UL ? EXCEPTION_EXECUTE_HANDLER : EXCEPTION_CONTINUE_SEARCH) {
        return 0;
    }
}
int wmain(int argc, wchar_t ** argv) {
    if (argc != 9) return 9;
    std::wstring original = argv[1], root = argv[2];
    std::wstring bin = root + L"\\bin", input = root + L"\\input\\public.txt";
    wchar_t cwd[32768] = {};
    DWORD count = GetCurrentDirectoryW(32768, cwd);
    if (!count || count >= 32768 || std::wstring(cwd) != bin) return 10;
    // Arguments are fixed by the repo harness. No user-selected path/command API.
    if (std::wstring(argv[3]) != L"..\\input\\spaced public.txt") return 11;
    if (std::wstring(argv[5]) != L"-f" || std::wstring(argv[6]) != L"../input/task.txt") return 13;
    int original_error = 0;
    bool original_narrow = narrow_read(utf8(original), legacy_prompt, &original_error);
    std::cout << "{\"status\":\"PUBLIC_FIXTURE_COMPLETE\",\"windows_acp\":" << GetACP()
              << ",\"original_narrow_errno\":" << original_error;
    flag("cwd_pinned", true);
    flag("original_wide_read", wide_read(original, legacy_prompt));
    flag("original_utf8_narrow_open_denied", !original_narrow && original_error == ENOENT);
    flag("copy_absolute_wide_read", wide_read(input, prompt));
    flag("copy_absolute_utf8_narrow_denied", !narrow_read(utf8(input), prompt));
    std::wstring slash = input;
    for (auto & c : slash) if (c == L'\\') c = L'/';
    flag("absolute_separator_does_not_fix_narrow", !narrow_read(utf8(slash), prompt));
    flag("absolute_slash_wide_read", wide_read(slash, prompt));
    flag("relative_backslash_read", narrow_read("..\\input\\public.txt", prompt));
    flag("relative_slash_read", narrow_read("../input/public.txt", prompt));
    flag("relative_dot_read", narrow_read(".\\..\\input\\public.txt", prompt));
    flag("fixed_native_plan_prompt_read", narrow_read(utf8(argv[6]), prompt));
    flag("fixed_framing_read", narrow_read(utf8(argv[6]), model_prompt + "\n"));
    std::ifstream framed_file(utf8(argv[6]));
    char framed_data[256]; framed_file.read(framed_data, sizeof(framed_data));
    std::string effective(framed_data, static_cast<size_t>(framed_file.gcount()));
    if (!effective.empty() && effective.back() == '\n') effective.pop_back();
    flag("file_parser_lf_exact", effective == model_prompt);
    std::string stop = "PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE";
    flag("fixed_stop_argument", std::wstring(argv[7]) == L"-r" && utf8(argv[8]) == stop);
    size_t marker_pos = effective.find(stop);
    flag("prompt_history_no_early_stop", marker_pos != std::string::npos &&
         effective.size() - marker_pos - stop.size() > 2);
    flag("quoted_argument_roundtrip", narrow_read(utf8(argv[3]), prompt));
    flag("lf_read", narrow_read("../input/public.txt", prompt));
    flag("crlf_text_normalized", narrow_read("../input/crlf.txt", prompt));
    flag("bom_is_content_not_open_failure", narrow_read("../input/bom.txt", std::string("\xef\xbb\xbf") + prompt));
    flag("wrong_cwd_relative_denied", !narrow_read("public.txt", prompt));
    flag("unlisted_read_denied", !wide_read(root + L"\\input\\unlisted.txt", "PUBLIC_UNLISTED"));
    flag("outside_read_denied", !wide_read(root + L"\\outside.txt", "PUBLIC_OUT_OF_SCOPE"));
    flag("writes_denied", denied_write(root + L"\\input\\write.txt") &&
         denied_write(root + L"\\bin\\write.txt") && denied_write(root + L"\\result\\write.txt"));
    HANDLE sentinel = reinterpret_cast<HANDLE>(_wcstoui64(argv[4], nullptr, 10));
    wchar_t name[32768] = {};
    DWORD n = sentinel_path(sentinel, name, 32768);
    std::wstring actual = n && n < 32768 ? name : L"";
    if (actual.rfind(L"\\\\?\\", 0) == 0) actual.erase(0, 4);
    flag("sentinel_excluded", actual != root + L"\\result\\sentinel");
    flag("stdout_pipe", GetFileType(GetStdHandle(STD_OUTPUT_HANDLE)) == FILE_TYPE_PIPE);
    flag("stderr_pipe", GetFileType(GetStdHandle(STD_ERROR_HANDLE)) == FILE_TYPE_PIPE);
    // Last checks deliberately change CWD. No need or permission to restore it:
    // this finite process terminates immediately, without model/other work.
    bool switched = SetCurrentDirectoryW(L"C:\\Windows\\System32") != 0;
    flag("cwd_switch_absolute_wide_still_reads", switched && wide_read(input, prompt));
    flag("cwd_switch_relative_denied", switched && !narrow_read("../input/public.txt", prompt));
    std::cout << "}\n";
    return 0;
}
