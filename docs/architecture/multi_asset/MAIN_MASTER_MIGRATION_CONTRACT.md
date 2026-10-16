# Canonical main / master Controlled Migration Contract — candidate.4 DESIGN ONLY

## Current / target authority

Current formal source remains master@9b5ab5fdd98744a7db45ec9f14b64ef1f324920f; GitHub default master. Originalmain@0cb0283b8c5f795f8da1672575cbb674945db73a retained; histories have no common ancestor. localP00@2634717b1443eb95fa0fde4d5d987347ef2160e8 aheadremoteP00d2bd7e9…sixcommits remains candidate. Long-term Human target is main, migration PLANNED_NOT_EXECUTED. No reviewedcandidate/source bundle publicupload or P00candidate merge is included.

## Required migration subject and owners

Existing Architect/Integrator produce exact preservation refs/graph/tree manifests and compare formalmain/master overlap. Existing IndependentReviewer reviews protectedacceptedblobs/privacy/CI/entrypoint/sourcebindings; Human provides exact integration/publication grant; Publisher only materializes reviewed graph/tree. Candidate preservation commits/working trees are separately inventoried, not materialized into formal target just because retained.

## Minimal recoverable method (proposal, not shell execution)

1. Re-read exact current refs/default/remotes/worktrees/dirty state and remote lease. Capture main/master/P00 sixcommits/neededbranches/worktree evidence in authorized private preservation set; prove object/ref reachability without forcing or deleting.
2. Prepare temporary integration subject under separately authorized refs. Proposed graph has both originalmain and acceptedmaster as parents; tree contains only formally acceptedmaster plus explicitly reviewed originalmain dispositions. This preserves both histories and makes publication a fast-forward descendant of originalmain. Do not use unrelated-history automatic merge as routine resolution; every overlapping/deleted initial file has disposition. UnacceptedP00/SQLRF01/Automation candidates excluded unless later separate exact adoption.
3. Reviewer validates graph parents, complete protectedblob equality, public source allowlist/no private captures, all main/master CI/docs/WORK/default-ref consumers, check repo-rule compatibility. Human approves exact integration subject/tree/parents/receipt. No sourceintegration itself createsArchitectureAcceptance.
4. AuthorizedPublisher attempts ordinary guarded publication onto expectedmainhead; if remote changes STOP/CONFLICT, neverforce/reset. Timeout unknown query remotecommit/tree/ref and receipt, never double-create success. After exactverification only authorizedsettings operation may change default to main and scoped localtracking/WORKentry successor. Originalmaster/main historicalrefs/receipts stay retrievable.
5. Verification must prove newmain descends both pinned histories, preserved acceptedblob tree, CI/contextentrances/tags/references/source manifests/readers coherent; WORKreads verifiedformalcontext. Failure beforepublication leavescurrentmasterauthority. Publicationunknown RECONCILIATION_REQUIRED; failureaftersettings restore authorized default/tracking to priorverified master as separate audited reversiblestep, no history deletion. MigrationCOMPLETE only after exactwitness+Humanadoption, not by branchlabel.

## Stop / authority / privacy

This proposal performs no Gitobjects/refs/branch/settings modifications. GitHubpermissions/adminflag/readaccess does notgrant Merge/Push. No Secrets/privatehistory/PublicGitexport. Expectedbaseline drifts -> only migration subject stops; other boundedcandidate design continues. Preservation hash proves bytes, not allrecoveryavailability. Publication/restore tests require laterboundedgrant.
