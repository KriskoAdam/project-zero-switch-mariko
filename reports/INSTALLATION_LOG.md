# Installation log

## Before the changes

- Confirmed: macOS 27.0.1 / arm64, Homebrew, Git 2.54.0, Python 3.14.7, Node 24.22.2, npm 11.19.1, Apple Clang.
- Missing: CMake, Ninja, LLVM, pkgconf/pkg-config, Java, Ghidra.
- Homebrew API provided available versions and SHA-256 arm64 bottle for required packages.
- The first attempt to brew install was rejected due to an unauthorized write to the Homebrew directories. After the explicit consent of the user, write permission was granted to Homebrew and cache paths within the session. Neither sudo nor changing system security settings were used.
- Started installation: cmake, ninja, llvm, pkgconf, openjdk@25, ghidra. The result will be added after the end.

## Python

- Created isolated .venv in the project.
- Started pip update in venv and install requirements.txt.
- The result and exact versions will be added after the end.

## Safety boundaries

Nothing was done on the console. No firmware or dumps were downloaded, no keys were used, no partitions were modified, no payloads were launched, no downgrade was performed.


## Completed installations and inspection

- Homebrew: CMake 4.4.5, Ninja 1.13.2, LLVM 23.1.4 + z3 5.3.3, pkgconf 3.0.10, OpenJDK 25.0.5.0.3.
- Node.js 24.22.2 already existed; confirmed LTS codename Krypton. Git/Python/Apple Clang preserved.
- REA diagnostics required Ghidra 12.1.x; Homebrew offered 12.2, so this version was removed before the workflow was finalized. Downloaded official Ghidra 12.1.4 archive from NSA GitHub; SHA-256 matches the official release. Home folder is tools/ghidra_12.1.4_PUBLIC.
- NSA archive did not contain mac_arm_64 native decompiler. The official task ./gradlew buildNatives has successfully built native components for Mac arm64 (BUILD SUCCESSFUL).
- Python venv created in .venv; pip 26.2.2; dependencies: capstone 5.0.9, pyelftools 0.33, lief 1.0.0, construct 2.10.70. pip check without errors.
- npx rea-agents@latest doctor could not be downloaded via npm registry (DNS/network ENOTFOUND). Used already installed official REA 6.8.0 from Codex npm cache; doctor CLI ran successfully. Codex registration/skill aligned; Ghidra/JDK/native checks passed after entering env.
- Updated existing [mcp_servers.rea.env] section in ~/.codex/config.toml with JAVA_HOME, GHIDRA_INSTALL_DIR and PATH. Codex must be restarted to get env to live REA server; we did not restart the live server.
- Scope validation: REA MCP tools answer in this Codex chat; Codex subagent support confirmed by five completed research delegations.
- REA firmware analysis/extraction provider is unsupported_host on this macOS. No target artifact is supplied; therefore, no binary analysis of the Switch firmware took place.

- After compilation, REA doctor for Ghidra 12.1.4, JDK 25, native decompiler and headless path went through. analyzeHeadless --help started analyzer and printed usage; exit 1 was expected because no project or input was specified.
- Final check_environment.sh and pip check passed; pip packages were imported in venv. The pip cache was not writable, so the cache was automatically turned off; system Python was not used to install dependencies.

## Research after the setup is complete

After installation, NH Guide, ns2jb author/repository, Nintendo security advisory, and Switchbrew 23.0.0 were re-verified for current compatibility. No new publicly reproducible chain was found for Mariko + HOS 23.0.1. Updated resolution: ns2jb WebKit path refers to Switch 2 and did not demonstrate sysmodule execution; the author's Switch 1 test is not specified by revision/FW.
