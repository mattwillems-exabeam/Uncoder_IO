"""
Uncoder IO Community Edition License
-----------------------------------------------------------------
Copyright (c) 2024 SOC Prime, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------
"""

from app.translator.core.custom_types.values import ValueType
from app.translator.core.escape_manager import EscapeManager
from app.translator.core.models.escape_details import EscapeDetails


class LogRhythmAIEEscapeManager(EscapeManager):
    """
    Character escaping for LogRhythm AIE regex patterns.

    SIGMA wildcards (* and ?) are converted to regex (.* and .)
    """

    def escape_regex_chars(self, value: str) -> str:
        """
        Escape regex special characters, preserving SIGMA wildcards.

        Examples:
        - 'mimikatz.exe' → 'mimikatz\\.exe'
        - '*mimikatz*' → '.*mimikatz.*' (wildcards converted)
        - 'C:\\Windows\\System32' → 'C:\\\\Windows\\\\System32'
        """
        # First escape regex metacharacters (except * and ? which are SIGMA wildcards)
        escaped = value
        for char in ['.', '^', '$', '+', '{', '}', '[', ']', '\\', '|', '(', ')']:
            escaped = escaped.replace(char, '\\' + char)

        # Now convert SIGMA wildcards to regex
        # * = zero or more characters → .*
        # ? = exactly one character → .
        escaped = escaped.replace('*', '.*').replace('?', '.')

        return escaped

    def escape_field_value(self, value: str, value_type: ValueType = None) -> str:
        """
        Escape field value based on type.

        For regex values (contains, startswith, endswith), escape regex chars.
        For exact matches, escape as needed.
        """
        if value_type in [ValueType.regex_value, ValueType.wildcard]:
            return self.escape_regex_chars(value)

        # For exact matches, still need to escape some chars if used in regex context
        # But this depends on how Uncoder core handles it
        return value

    def escape_manager(self, escape_details: EscapeDetails) -> str:
        """Main escape manager entry point"""
        if escape_details.pattern:
            return self.escape_regex_chars(escape_details.pattern)
        return escape_details.pattern or ""


# Create singleton instance
logrhythm_aie_escape_manager = LogRhythmAIEEscapeManager()
