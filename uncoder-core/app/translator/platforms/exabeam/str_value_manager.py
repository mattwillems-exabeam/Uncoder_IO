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
from typing import Optional
from app.translator.platforms.exabeam.escape_manager import ExabeamAnalyticsEscapeManager
from app.translator.core.custom_types.values import ValueType
from app.translator.core.str_value_manager import (
    StrValue,
    StrValueManager,
)

class ExabeamAnalyticsStrValueManager(StrValueManager):
    escape_manager = ExabeamAnalyticsEscapeManager()
    
    def from_str_to_container(
        self,
        value: str,
        value_type: str = ValueType.value,  # noqa: ARG002
        escape_symbol: Optional[str] = None,  # noqa: ARG002
    ) -> StrValue:
        split = []
        for char in value:
            split.append(char)


        return StrValue(value, self._concat(split))
exabeam_analytics_str_value_manager = ExabeamAnalyticsStrValueManager()