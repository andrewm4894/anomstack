"""
Test for Docusaurus documentation build and link validation.
Uses Docusaurus's native broken link detection.
"""
import subprocess
import os
import pytest
from pathlib import Path


def test_docusaurus_build_succeeds():
    """Test that Docusaurus can build the documentation without broken links."""
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / "docs"
    
    if not docs_dir.exists():
        pytest.skip("Docs directory not found")
    
    # Check if yarn/npm is available and node_modules exists
    if not (docs_dir / "node_modules").exists():
        pytest.skip("Node modules not installed. Run 'cd docs && yarn install' first.")
    
    # Run docusaurus build which includes built-in link checking
    try:
        result = subprocess.run(
            ["yarn", "build"],
            cwd=docs_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = "Docusaurus build failed (likely due to broken links):\n"
            error_msg += f"STDOUT:\n{result.stdout}\n"
            error_msg += f"STDERR:\n{result.stderr}\n"
            pytest.fail(error_msg)
            
    except subprocess.TimeoutExpired:
        pytest.fail("Docusaurus build timed out after 5 minutes")
    except FileNotFoundError:
        pytest.skip("yarn not available. Install Node.js and yarn to run this test.")


def test_architecture_grpc_section_exists():
    """Test that the gRPC opt-in section exists in ARCHITECTURE.md."""
    repo_root = Path(__file__).parent.parent
    architecture_file = repo_root / "ARCHITECTURE.md"
    
    if not architecture_file.exists():
        pytest.skip("ARCHITECTURE.md not found")
    
    with open(architecture_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that the gRPC section exists
    assert "### Advanced: gRPC Code Server (Optional)" in content, \
        "ARCHITECTURE.md should contain the gRPC opt-in section"
    
    # Check that it mentions the anchor that docs link to
    assert "advanced-grpc-code-server-optional" in content.lower().replace(' ', '-').replace(':', ''), \
        "gRPC section should be linkable with the expected anchor"


if __name__ == "__main__":
    # For manual testing without pytest
    import sys
    
    print("🔍 Testing Docusaurus documentation...")
    
    try:
        test_architecture_grpc_section_exists()
        print("✅ gRPC section test passed")
    except Exception as e:
        print(f"❌ gRPC section test failed: {e}")
        sys.exit(1)
    
    try:
        test_docusaurus_build_succeeds()
        print("✅ Docusaurus build test passed")
    except Exception as e:
        print(f"❌ Docusaurus build test failed: {e}")
        sys.exit(1)
    
    print("🎉 All documentation tests passed!")