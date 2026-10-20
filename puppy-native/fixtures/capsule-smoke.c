#include <stdio.h>
/* Build with x86_64-w64-mingw32-gcc -Os -o capsule-smoke.exe capsule-smoke.c
 * Guest probe requires the same marker on initial execution and relaunch.
 * This is a deterministic fixture, not evidence of guest execution.
 */
int main(void) {
    puts("VENVWIN_CAPSULE_EXE_OK");
    return 0;
}
