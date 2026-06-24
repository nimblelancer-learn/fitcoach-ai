# GitHub Issue Goal Workflow

This document defines the repository workflow for asking Codex to pick the
oldest open GitHub issue and execute it end to end in goal mode.

## Purpose

Use this when you want Codex to:

- inspect open GitHub issues with `gh`
- select the oldest issue by `createdAt`
- create a concrete execution plan
- implement the issue in the local repo
- run validation
- commit, push, create a PR, and merge when allowed
- document the work back on the issue
- close the issue

## Preconditions

Before running this workflow, make sure:

- `gh auth status` shows a logged-in account with repo access
- the local repo remote points at the intended GitHub repository
- the active account has permission to push branches, create PRs, comment on
  issues, and merge PRs if merge is expected
- any required local dependencies are already available, or you are willing to
  approve commands that need extra filesystem or network access

## Selection rule

Pick the issue with:

- `state == open`
- the earliest `createdAt` timestamp among open issues

If several issues exist, do not choose based on label or title unless the user
explicitly overrides the selection rule.

## Required execution mode

Run the workflow in goal mode and keep the goal active until the issue is
actually finished or genuinely blocked.

The goal should cover the full lifecycle:

- inspect issue
- extract requirements
- implement
- validate
- commit and push
- create PR
- merge if repository rules permit
- update issue metadata or evidence when possible
- comment documentation on the issue
- close the issue

## Standard workflow

1. Confirm repository state.
2. Verify `gh` authentication.
3. List open issues and sort by `createdAt`.
4. Open the oldest issue and read:
   - title
   - body
   - comments
   - labels
   - linked project items when available
5. Translate the issue into a concrete implementation plan.
6. Create a dedicated branch named after the issue.
7. Implement the required changes in the repo.
8. Add or update tests when behavior or artifact contracts change.
9. Run validation commands relevant to the change.
10. Commit with a scoped message.
11. Push the branch to `origin`.
12. Create a PR that links the issue with `Closes #<issue_number>` when closure
    on merge is desired.
13. Check PR mergeability and status checks.
14. Merge the PR if the repository rules allow it.
15. Update linked project fields such as `Evidence` when a linked project item
    actually exists and the account has permission.
16. Comment on the issue with:
    - what had to be done
    - what was implemented
    - why the approach was chosen
    - explanations of any new terms
    - validation results
17. Confirm the issue is closed.
18. Return the local repo to a clean state on `main`.

## Rules during execution

- Do not commit directly to `main` for issue work unless the user explicitly
  asks for that exception.
- Prefer a dedicated feature branch per issue.
- Do not assume a GitHub Project item exists for the issue.
- Check `projectItems` first before trying to update an `Evidence` field.
- If `projectItems` is empty, state clearly that no linked Project evidence
  field was available.
- If merge is blocked by checks, review rules, or permissions, stop at the
  highest completed stage and report the blocker clearly.
- Keep issue comments operational and repository-specific, not generic.

## Suggested command pattern

Typical commands used in this workflow:

```bash
gh auth status
gh issue list --state open --limit 100 --json number,title,createdAt,url,labels
gh issue view <issue_number> --json number,title,body,comments,labels,projectItems,url,createdAt,state
git switch -c issue-<issue_number>-<short-slug>
git status --short --branch
git add <paths>
git commit -m "<message>"
git push -u origin <branch>
gh pr create --base main --head <branch> --title "<title>" --body "<body>"
gh pr view <branch> --json number,url,state,mergeStateStatus,reviewDecision,statusCheckRollup
gh pr checks <pr_number>
gh pr merge <pr_number> --merge --delete-branch
gh issue comment <issue_number> --body-file <file>
gh issue view <issue_number> --json state,url
```

## Comment template

The issue follow-up comment should cover:

- implementation summary
- required work items from the issue
- reasoning behind the chosen approach
- short glossary for any new technical terms
- validation results
- project evidence update status

When shell quoting would be fragile, write the comment to a temporary markdown
file and post it with `gh issue comment --body-file`.

## Completion criteria

The workflow is complete only when all of these are true:

- the code or repository artifact requested by the issue exists
- relevant tests or validation commands have run
- the changes are committed and pushed
- a PR was created
- the PR was merged, unless blocked by repository policy or permissions
- the issue has a documentation comment
- the issue is closed, either automatically via PR closure keywords or manually

## Reusable prompt

Use this exact instruction when you want Codex to run the workflow again:

```text
Reference docs/github-issue-goal-workflow.md, use goal mode, get the oldest open GitHub issue by created date, and execute the workflow end to end until the issue is finished or clearly blocked.
```
