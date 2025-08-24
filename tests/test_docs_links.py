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
    
    # Check Node.js version compatibility
    try:
        node_result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if node_result.returncode == 0:
            node_version = node_result.stdout.strip().lstrip('v')
            major_version = int(node_version.split('.')[0])
            if major_version < 20:
                pytest.skip(f"Node.js version {node_version} is incompatible. Docusaurus requires Node.js >=20.0")
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pytest.skip("Could not check Node.js version. Install Node.js >=20.0 to run this test.")
    
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




if __name__ == "__main__":
    # For manual testing without pytest
    import sys
    
    print("🔍 Testing Docusaurus documentation...")
    
    try:
        test_docusaurus_build_succeeds()
        print("✅ Docusaurus build test passed")
    except pytest.skip.Exception as e:
        print(f"⏭️  Docusaurus build test skipped: {e}")
    except Exception as e:
        print(f"❌ Docusaurus build test failed: {e}")
        sys.exit(1)
    
    print("🎉 All documentation tests passed!")