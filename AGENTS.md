# AGENTS.md - J-TWAT Project Documentation

## Overview

**J-TWAT** (The Java Telnet Application for Trade Wars) is a Java-based telnet client specifically designed for connecting to Trade Wars game servers.

- **Version**: 0.951
- **Original Author**: badboy (badboy@goosemoose.com)
- **Website**: http://www.goosemoose.com/~jtwat
- **License**: GNU General Public License v2+
- **Original Release**: April 13, 2001
- **Source**: http://j-twat.sourceforge.net/

### Main Features
- Telnet client with VT320 terminal emulation
- Plugin-based architecture (Socket, Telnet, TW, TWStatus, Terminal)
- Pre-configured connections to popular Trade Wars servers
- Customizable terminal appearance and behavior
- Cross-platform Java implementation

### Key Technologies
- Java 1.1+ (originally designed for Java 1.3)
- JTA (Java Telnet Application) framework
- Plugin system using `de.mud.jta.plugin`
- VT320 terminal emulation

## Folder Structure

The project has a flat directory structure:

```
jtwat/
├── jtwat.jar              # Main application archive
├── TWLaunch.class         # Launcher class file
├── jtwat.conf             # Main configuration file
├── jtwat.bat              # Windows launch script
├── .jtwataddresses        # Pre-configured server addresses
├── install.txt            # Installation instructions
├── version                # Version number (0.951)
└── agent-template.md      # Documentation template
```

## Core Behaviors & Patterns

### Configuration System
- **Plugin Loading**: Plugins are loaded via the `plugins` property in [jtwat.conf](jtwat.conf)
  - Current plugins: `Socket,Telnet,TW,TWStatus,Terminal`
  - Plugin path: `de.mud.jta.plugin`

- **Layout Management**: BorderLayout-based UI structure
  - Terminal component: Center position
  - TWStatus component: South position
  - TW component: North position

### Connection Management
- Pre-configured servers stored in [.jtwataddresses](.jtwataddresses)
- Format: `ServerName\tHostname\tPort`
- Includes timeout settings (120 seconds default)
- Disconnect command: `exit\n`

### Terminal Behavior
- **Emulation**: VT320 terminal with IBM mode enabled
- **Display**: 80x24 character buffer, 1000 line scrollback
- **Colors**: White text on black background (#ffffff on #000000)
- **Font**: Courier, plain style, 12pt

## Conventions

### File Organization
- Configuration uses `.conf` extension with property-style format
- Class files and JAR kept in project root
- Address book uses dot-prefix (`.jtwataddresses`)

### Configuration Format
```properties
# Comment style: hash prefix
property.name = value
nested.property = value
```

### Naming Conventions
- Java packages: lowercase with dots (`de.mud.jta.plugin`)
- Components: CamelCase (`TWStatus`, `Terminal`)
- Config properties: dot-separated lowercase

## Platform-Specific Considerations

### macOS Compatibility

The original [jtwat.bat](jtwat.bat) script uses Windows-style classpath separators which **will not work on macOS/Unix**.

**Original (Windows)**:
```batch
java -cp .;jtwat.jar TWLaunch
```

**Required for macOS/Unix**:
```bash
java -cp .:jtwat.jar TWLaunch
```

#### Key Differences
- **Classpath separator**:
  - Windows: semicolon (`;`)
  - macOS/Unix: colon (`:`)

#### Launch Methods for macOS

**Option 1: Create a shell script** (jtwat.sh)
```bash
#!/bin/bash
java -cp .:jtwat.jar TWLaunch
```
Then make it executable: `chmod +x jtwat.sh`

**Option 2: Direct command**
```bash
java -cp .:jtwat.jar TWLaunch
```

**Option 3: Create an alias** (in ~/.zshrc or ~/.bash_profile)
```bash
alias jtwat='java -cp .:jtwat.jar TWLaunch'
```

### Java Version Requirements
- **Minimum**: Java 1.1 (JDK or JRE)
- **Recommended**: Java 1.2 or greater
- **Originally tested**: Java 1.3 Runtime (2001)
- **Tested on macOS**: ✅ Java 25.0.1 (OpenJDK Temurin) - Works!

To check your Java version on macOS:
```bash
java --version
```

**Compatibility Notes:**
- Despite being built for Java 1.3, J-TWAT runs successfully on Java 25
- Some non-fatal errors occur (version check failure, missing optional classes)
- Core functionality remains intact

## Working Agreements

### When Making Changes
- **Preserve compatibility**: This is legacy software from 2001
- **Minimal modifications**: Only change what's necessary for functionality
- **Document platform differences**: Note any macOS-specific changes
- **Test connections**: Verify telnet functionality to game servers

### Configuration Management
- Edit [jtwat.conf](jtwat.conf) for terminal settings and plugin configuration
- Edit [.jtwataddresses](.jtwataddresses) to add/modify server connections
- Do not modify the JAR file unless absolutely necessary

## When Extending

### Adding New Server Connections
Edit [.jtwataddresses](.jtwataddresses) with the format:
```
ServerName<TAB>hostname<TAB>port
```

### Customizing Terminal Appearance
Edit [jtwat.conf](jtwat.conf) under the "Terminal defaults" section:
- `Terminal.foreground`: Text color (hex format)
- `Terminal.background`: Background color (hex format)
- `Terminal.font`: Font family
- `Terminal.fontSize`: Font size in points

### Plugin System
Plugins are loaded from the `plugins` property:
```properties
plugins = Socket,Telnet,TW,TWStatus,Terminal
pluginPath = de.mud.jta.plugin
```

To add new plugins:
1. Add the plugin class to the classpath
2. Update the `plugins` property
3. Configure layout if the plugin has UI components

## Known Issues & Notes

### macOS-Specific
- **Classpath separator**: Must use `:` instead of `;`
- **Line endings**: May need to convert CRLF to LF for shell scripts
- **Java availability**: macOS may require installing Java separately

### Known Non-Fatal Errors
When launching on modern Java (tested with Java 25):

1. **"Error Connecting to Version Control!!!"**
   - Cause: Tries to connect to a 2001-era update server that no longer exists
   - Impact: None - version checking is non-essential
   - Error: `NumberFormatException: For input string: "<html>"`

2. **"ClassNotFoundException: TWHelp.PhotonPlanetScript"**
   - Cause: Optional script helper class not included in distribution
   - Impact: Some advanced scripting features may not work
   - Workaround: None needed for basic telnet functionality

These errors are **non-fatal** - the application continues to load and basic telnet functionality works.

### Critical Compatibility Issue: Java 25 Parser Bug ⚠️

**The Trade Wars helper features are BROKEN on Java 25** due to a parser crash:

```
ArrayIndexOutOfBoundsException: Index 65533 out of bounds for length 256
at TWHelp.Yylex.yylex(Unknown Source)
```

**What Works:**
- ✅ **Telnet terminal** - Full functionality for connecting and playing Trade Wars
- ✅ **Basic terminal emulation** - VT320 terminal works correctly

**What Doesn't Work:**
- ❌ **"Update Database" button** - Parser crashes, can't capture game data
- ❌ **Port Pair Trade script** - Requires parsed data (results in NullPointerException)
- ❌ **Ship Explore script** - Requires parsed data (results in NullPointerException)
- ❌ **Analysis tools** - All depend on the broken parser
- ❌ **All automated helpers** - Cannot extract game information

**Root Cause:**
The lexical analyzer (`Yylex.yylex`) has a character encoding/casting bug when running on Java 25. The code was written for Java 1.3 (2001) and relies on character handling behavior that changed in later Java versions.

**Workarounds:**
1. **Use as telnet client only** - Works perfectly, just no automation
2. **Try older Java** - Install Java 8 or 11 and run with that instead:
   ```bash
   # Example with Java 11
   brew install openjdk@11
   /usr/local/opt/openjdk@11/bin/java -cp .:jtwat.jar TWLaunch
   ```
3. **Use alternative tools** - Look for modern Trade Wars clients/helpers

### Legacy Considerations
- This is a 25-year-old Java application (2001)
- Some server addresses may be outdated
- Original Java applet functionality may not work in modern browsers
- Terminal emulation is VT320, which should be widely compatible

## Pre-configured Servers

| Server Name | Hostname | Port |
|------------|----------|------|
| GooseMoose.com | 198.76.185.2 | 1979 |
| The Stardock | thestardock.com | 23 |
| SilverWings | tradewarsbbs.com | 23 |
| swath | twgs.swath.net | 23 |

## Usage Guide

### Basic Telnet Terminal (Fully Working)

1. **Launch J-TWAT**:
   ```bash
   ./jtwat.sh
   ```

2. **Connect to a Trade Wars server**:
   - Select a server from the dropdown menu (top of window)
   - Pre-configured servers are loaded from [.jtwataddresses](.jtwataddresses)
   - Click "Connect" or press Enter

3. **Play Trade Wars**:
   - Use the terminal window to play the game normally
   - All keyboard input works
   - Terminal emulation (VT320) handles game display correctly

4. **Disconnect**:
   - Type the game's quit command
   - Or close the J-TWAT window

### Trade Wars Helper Features (Broken on Java 25)

The following features **do not work** with Java 25 due to parser bugs:

- **Update Database**: Supposed to parse game data from terminal output
- **Port Pair Trade**: Finds profitable trading routes (requires database)
- **Ship Explore**: Automated sector exploration (requires database)
- **Analysis Tools**: Port pair analysis, evil pair detection, etc.
- **All Scripts**: Automated gameplay helpers

**Error you'll see**: `ArrayIndexOutOfBoundsException` in console, buttons do nothing or show errors.

**To use these features**: Try running with Java 8 or Java 11 instead of Java 25.

### Adding New Server Addresses

Edit [.jtwataddresses](.jtwataddresses) with tab-separated values:
```
ServerName<TAB>hostname<TAB>port
```

Example:
```
MyServer	example.com	23
```

## Quick Start for macOS

1. **Ensure Java is installed**:
   ```bash
   java -version
   ```
   If not installed, download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or use Homebrew:
   ```bash
   brew install openjdk
   ```

2. **Navigate to the jtwat directory**:
   ```bash
   cd /Users/chantal/Documents/GitHub/jtwat
   ```

3. **Launch J-TWAT**:
   ```bash
   java -cp .:jtwat.jar TWLaunch
   ```

4. **Or create a launch script**:
   ```bash
   echo '#!/bin/bash' > jtwat.sh
   echo 'java -cp .:jtwat.jar TWLaunch' >> jtwat.sh
   chmod +x jtwat.sh
   ./jtwat.sh
   ```

## Resources

- Original forum discussion: https://classictw.com/viewtopic.php?t=12819&p=105888
- Original website: http://www.goosemoose.com/~jtwat
- SourceForge project: http://j-twat.sourceforge.net/

## License

This software is licensed under the GNU General Public License version 2 or later.
See the license header in [jtwat.conf](jtwat.conf) for full details.
