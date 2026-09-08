# Working with this pet collection

Read README.md first. This repository contains existing user-approved art; preserve
pet.json and referenced spritesheet bytes and sprite versions when syncing.
Use pets.py to install/export; default to conflict detection, and ask which copy
to retain when a conflict has not already been resolved by the user.
Never upload Codex config, sessions, credentials, logs, or unrelated local files.
Before uploading: pull --ff-only, export selected pets, validate, inspect the diff,
then commit and push when the user has requested upload/sync. Never force-push.
An install request authorizes copying pets into CODEX_HOME/pets (default ~/.codex/pets).
An upload request authorizes exporting local pets and pushing to this repository.
