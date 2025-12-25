#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sys import version_info
from .db import db
import git

__all__ = [
    "modules_help",
    "requirements_list",
    "python_version",
    "prefix",
    "userbot_version",
]


modules_help = {}
requirements_list = []

python_version = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"

prefix = "." # Default prefix, will be loaded dynamically in commands if needed or we must init it differently.

# Git logic removed for Lite version stability
userbot_version = "v1.0.0"