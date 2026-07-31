# Hermes Agent core update available

**Issue**

The installed Hermes Agent reports that its Git installation is 121 commits behind upstream.

**Location**

`/opt/hermes-agent`

**Severity**

low

**Context**

`hermes --version` reported Hermes Agent v0.19.0 (2026.7.20), upstream commit `14db1a99`, and an available update. Updating the Hermes core is outside this task, which only deploys the approved planning-workflow skill files to the active profile. A core update could affect bundled skills, plugins, and runtime behavior and should not be combined silently with this scoped deployment.

**Suggested Fix**

Schedule a separate Hermes core update window. Preserve local changes, run the supported `hermes update` flow, restart the owning runtime boundary, and verify `hermes --version`, status, plugins, tools, and skills afterward.
