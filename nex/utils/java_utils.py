import os
import subprocess
import platform
from typing import Optional

def find_java_executable() -> Optional[str]:
    """Find a Java executable on the system."""
    # First check if JAVA_HOME is set
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_path = os.path.join(java_home, "bin", "java" + (".exe" if platform.system() == "Windows" else ""))
        if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
            return java_path
    
    # Try to use the java command directly
    try:
        # Check if java is in PATH
        if platform.system() == "Windows":
            # On Windows, use where
            result = subprocess.run(["where", "java"], capture_output=True, text=True, check=True)
            paths = result.stdout.strip().split("\n")
            if paths:
                return paths[0]
        else:
            # On Unix-like systems, use which
            result = subprocess.run(["which", "java"], capture_output=True, text=True, check=True)
            path = result.stdout.strip()
            if path:
                return path
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Platform-specific default locations
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        
        # Common installation paths for Java on Windows
        possible_paths = [
            os.path.join(program_files, "Java"),
            os.path.join(program_files_x86, "Java"),
            os.path.join(program_files, "AdoptOpenJDK"),
            os.path.join(program_files_x86, "AdoptOpenJDK"),
            r"C:\Program Files\Eclipse Adoptium"
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for dir_name in sorted(os.listdir(base_path), reverse=True):
                    if "jdk" in dir_name.lower() or "jre" in dir_name.lower():
                        java_path = os.path.join(base_path, dir_name, "bin", "java.exe")
                        if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
                            return java_path
    
    elif platform.system() == "Darwin":  # macOS
        # Common installation paths for Java on macOS
        possible_paths = [
            "/Library/Java/JavaVirtualMachines",
            "/System/Library/Java/JavaVirtualMachines",
            "/usr/libexec/java_home"
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                if base_path == "/usr/libexec/java_home":
                    try:
                        result = subprocess.run([base_path, "-v", "1.8+"], 
                                               capture_output=True, text=True, check=True)
                        java_home = result.stdout.strip()
                        java_path = os.path.join(java_home, "bin", "java")
                        if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
                            return java_path
                    except subprocess.SubprocessError:
                        pass
                else:
                    for dir_name in sorted(os.listdir(base_path), reverse=True):
                        java_path = os.path.join(base_path, dir_name, "Contents", "Home", "bin", "java")
                        if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
                            return java_path
    
    else:  # Linux and other Unix-like systems
        # Common installation paths for Java on Linux
        possible_paths = [
            "/usr/lib/jvm",
            "/usr/java",
            "/opt/java"
        ]
        
        for base_path in possible_paths:
            if os.path.exists(base_path):
                for dir_name in sorted(os.listdir(base_path), reverse=True):
                    if "jdk" in dir_name.lower() or "jre" in dir_name.lower():
                        java_path = os.path.join(base_path, dir_name, "bin", "java")
                        if os.path.isfile(java_path) and os.access(java_path, os.X_OK):
                            return java_path
    
    # Java not found
    return None


def verify_java_version(java_path: str, min_version: int = 17) -> bool:
    """Verify that the Java executable meets minimum version requirements."""
    try:
        result = subprocess.run([java_path, "-version"], 
                               capture_output=True, text=True, stderr=subprocess.STDOUT)
        
        # Parse Java version from output
        version_output = result.stdout.strip()
        
        # Extract the version number using a common pattern
        import re
        version_pattern = r'version "([^"]+)"'
        match = re.search(version_pattern, version_output)
        
        if match:
            version_str = match.group(1)
            
            # Handle different version formats
            if version_str.startswith("1."):
                # Older format like "1.8.0_292"
                major_version = int(version_str.split(".")[1])
            else:
                # Newer format like "11.0.11" or "17.0.2"
                major_version = int(version_str.split(".")[0])
            
            return major_version >= min_version
        
        return False
        
    except (subprocess.SubprocessError, ValueError, IndexError):
        return False