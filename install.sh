#!/bin/bash
set -e

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MCP Agile Flow Installer ===${NC}"
echo -e "${YELLOW}This script will install MCP Agile Flow from GitHub and configure it for your system${NC}\n"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}UV is not installed. Please install UV first.${NC}"
    echo -e "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Check if custom SSH key exists
SSH_KEY_PATH="$HOME/.ssh/id_ed25519_github"
GITHUB_REPO="git@github.com:smian0/mcp-agile-flow.git"
USE_SSH=true

# Function to ask user for input
ask() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    local response

    if [ -n "$default" ]; then
        prompt="$prompt [$default]"
    fi

    echo -e "${YELLOW}$prompt${NC}"
    read -r response

    if [ -z "$response" ] && [ -n "$default" ]; then
        response="$default"
    fi

    eval "$var_name=\"$response\""
}

# Ask for GitHub repository
ask "GitHub repository (format: username/repo)" "smian0/mcp-agile-flow" GITHUB_REPO_INPUT
GITHUB_REPO="${GITHUB_REPO_INPUT}"

# Ask for auth method
echo -e "${YELLOW}Authentication method:${NC}"
echo "1. SSH (recommended if you have SSH keys configured)"
echo "2. HTTPS with personal access token"
read -r auth_choice

if [ "$auth_choice" = "2" ]; then
    USE_SSH=false
    ask "GitHub username" "" GITHUB_USERNAME
    ask "GitHub personal access token" "" GITHUB_TOKEN
fi

echo -e "\n${BLUE}=== Installing MCP Agile Flow ===${NC}"

# Install the package
if [ "$USE_SSH" = true ]; then
    echo "Installing via SSH..."
    
    # Check if custom SSH key exists
    if [ -f "$SSH_KEY_PATH" ]; then
        echo "Using SSH key: $SSH_KEY_PATH"
        GIT_SSH_COMMAND="ssh -i $SSH_KEY_PATH" uv pip install "git+ssh://git@github.com/$GITHUB_REPO"
    else
        echo "Using default SSH configuration"
        uv pip install "git+ssh://git@github.com/$GITHUB_REPO"
    fi
else
    echo "Installing via HTTPS..."
    uv pip install "git+https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com/$GITHUB_REPO"
fi

echo -e "\n${GREEN}✓ MCP Agile Flow installed successfully!${NC}"

# Configure MCP
echo -e "\n${BLUE}=== Configuring MCP ===${NC}"

# Get Python path
PYTHON_PATH=$(which python)
echo "Using Python at: $PYTHON_PATH"

# Get UVX path
UVX_PATH=$(which uvx)
echo "Using UVX at: $UVX_PATH"

# Create base MCP config
create_mcp_config() {
    local config_type="$1"
    local config_file="$2"
    
    if [ "$config_type" = "python" ]; then
        cat > "$config_file" << EOF
{
  "mcpServers": {
    "agile-flow": {
      "command": "$PYTHON_PATH",
      "args": ["-m", "mcp_agile_flow.server"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings", "read_graph", "get_mermaid_diagram"],
      "timeout": 30
    }
  }
}
EOF
    elif [ "$config_type" = "uvx" ]; then
        cat > "$config_file" << EOF
{
  "mcpServers": {
    "agile-flow": {
      "command": "$UVX_PATH",
      "args": ["--with-editable", ".", "python", "-m", "mcp_agile_flow.server"],
      "disabled": false,
      "autoApprove": ["initialize-ide-rules", "get-project-settings", "read_graph", "get_mermaid_diagram"],
      "timeout": 30
    }
  }
}
EOF
    fi
}

# Detect IDEs and install configs
CURSOR_CONFIG_DIR="$HOME/.cursor/mcp-experimental"
VSCODE_CONFIG_DIR="$HOME/.vscode/mcp"
WINDSURF_CONFIG_DIR="$HOME/.windsurf/mcp"
CLINE_CONFIG_DIR="$HOME/.cline/mcp"
DEFAULT_MCP_DIR="$HOME/.mcp"

# Create MCP directories if they don't exist
mkdir -p "$DEFAULT_MCP_DIR"

# Ask which configuration to use
echo -e "${YELLOW}Configuration type:${NC}"
echo "1. Python direct (recommended)"
echo "2. UVX (experimental)"
read -r config_choice

if [ "$config_choice" = "2" ]; then
    CONFIG_TYPE="uvx"
else
    CONFIG_TYPE="python"
fi

# Create default configuration
create_mcp_config "$CONFIG_TYPE" "$DEFAULT_MCP_DIR/config.json"
echo -e "${GREEN}✓ MCP configuration created at: $DEFAULT_MCP_DIR/config.json${NC}"

# Check for Cursor
if [ -d "$HOME/.cursor" ]; then
    echo -e "\n${BLUE}Cursor IDE detected${NC}"
    mkdir -p "$CURSOR_CONFIG_DIR"
    create_mcp_config "$CONFIG_TYPE" "$CURSOR_CONFIG_DIR/config.json"
    echo -e "${GREEN}✓ MCP configuration installed for Cursor IDE${NC}"
fi

# Check for VS Code
if [ -d "$HOME/.vscode" ]; then
    echo -e "\n${BLUE}VS Code detected${NC}"
    mkdir -p "$VSCODE_CONFIG_DIR"
    create_mcp_config "$CONFIG_TYPE" "$VSCODE_CONFIG_DIR/config.json"
    echo -e "${GREEN}✓ MCP configuration installed for VS Code${NC}"
fi

# Check for Windsurf
if [ -d "$HOME/.windsurf" ]; then
    echo -e "\n${BLUE}Windsurf detected${NC}"
    mkdir -p "$WINDSURF_CONFIG_DIR"
    create_mcp_config "$CONFIG_TYPE" "$WINDSURF_CONFIG_DIR/config.json"
    echo -e "${GREEN}✓ MCP configuration installed for Windsurf${NC}"
fi

# Check for Cline
if [ -d "$HOME/.cline" ]; then
    echo -e "\n${BLUE}Cline detected${NC}"
    mkdir -p "$CLINE_CONFIG_DIR"
    create_mcp_config "$CONFIG_TYPE" "$CLINE_CONFIG_DIR/config.json"
    echo -e "${GREEN}✓ MCP configuration installed for Cline${NC}"
fi

# Print instructions
echo -e "\n${BLUE}=== Next Steps ===${NC}"
echo -e "1. Restart your IDE to apply the changes"
echo -e "2. You can now use MCP Agile Flow tools in your IDE"
echo -e "\n${GREEN}Installation complete!${NC}"

# Create quick command for running server
echo -e "\n${BLUE}=== Creating Quick Command ===${NC}"
SCRIPT_DIR="$HOME/.local/bin"
mkdir -p "$SCRIPT_DIR"

cat > "$SCRIPT_DIR/mcp-agile-flow" << EOF
#!/bin/bash
$PYTHON_PATH -m mcp_agile_flow.server "\$@"
EOF

chmod +x "$SCRIPT_DIR/mcp-agile-flow"
echo -e "${GREEN}✓ Quick command created: mcp-agile-flow${NC}"
echo -e "${YELLOW}Make sure $SCRIPT_DIR is in your PATH to use this command${NC}"

# Check if the user wants to install MCP inspector
echo -e "\n${BLUE}=== MCP Inspector (Optional) ===${NC}"
echo -e "${YELLOW}Would you like to install the MCP inspector for debugging? [y/N]${NC}"
read -r install_inspector

if [[ "$install_inspector" =~ ^[Yy]$ ]]; then
    if command -v npm &> /dev/null; then
        echo "Installing MCP inspector..."
        npm install -g @modelcontextprotocol/inspector
        
        # Create debug script
        cat > "$SCRIPT_DIR/mcp-agile-flow-debug" << EOF
#!/bin/bash
npx @modelcontextprotocol/inspector $PYTHON_PATH -m mcp_agile_flow.server "\$@"
EOF
        chmod +x "$SCRIPT_DIR/mcp-agile-flow-debug"
        echo -e "${GREEN}✓ Debug command created: mcp-agile-flow-debug${NC}"
    else
        echo -e "${RED}npm is not installed. MCP inspector requires npm.${NC}"
        echo -e "You can install it later with: npm install -g @modelcontextprotocol/inspector"
    fi
fi

echo -e "\n${GREEN}Installation complete!${NC}" 