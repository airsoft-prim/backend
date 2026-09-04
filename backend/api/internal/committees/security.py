from fastapi import Security

from backend.general.enums import UserRole
from backend.protection import RequireBearerToken

access_policy = RequireBearerToken()

COMMON_COMMITTEE_SEC = Security(access_policy, scopes=UserRole.PLAYER.equal_or_higher())
