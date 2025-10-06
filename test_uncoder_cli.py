#!/usr/bin/env python3
"""
Simple CLI test for Uncoder.io LogRhythm AIE platform
"""
import sys
import os

# Add uncoder-core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'uncoder-core'))

from app.translator.core.models.platform_details import PlatformDetails
from app.translator.managers import render_manager, parser_manager
from app.translator.platforms.logrhythm_aie.renders.logrhythm_aie_rule import LogRhythmAIERuleRender

def convert_sigma_to_aie(sigma_file, output_file=None):
    """Convert SIGMA YAML to LogRhythm AIE JSON"""

    # Read SIGMA file
    with open(sigma_file, 'r') as f:
        sigma_content = f.read()

    # Get SIGMA parser
    sigma_parser = parser_manager.get_parser(platform_name='sigma')

    # Parse SIGMA rule
    parsed = sigma_parser.parse(text=sigma_content)

    # Get LogRhythm AIE renderer
    aie_renderer = LogRhythmAIERuleRender()

    # Generate AIE JSON
    aie_json = aie_renderer.generate(None, parsed)

    # Output
    if output_file:
        with open(output_file, 'w') as f:
            f.write(aie_json)
        print(f"Converted {sigma_file} -> {output_file}")
    else:
        print(aie_json)

    return aie_json

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_uncoder_cli.py <sigma_file> [output_file]")
        sys.exit(1)

    sigma_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_sigma_to_aie(sigma_file, output_file)
