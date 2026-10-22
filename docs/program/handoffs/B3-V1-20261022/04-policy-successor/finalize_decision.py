import pathlib,json,hashlib,datetime
O=pathlib.Path(__file__).parent;V=O.parent;R=pathlib.Path('D:/00_Learn/量化交易/Code/futures_trading_system')
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(n,x):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
cm=O/'candidate/CANDIDATE_MANIFEST.json';rm=O/'fresh-review/REVIEW_OUTPUT_MANIFEST.json'
assert h(cm)=='091fd1e697a32f65c4a65f6b493175d6467671e08c44945c28ec750575942421'
assert h(rm)=='1e6f08b7f4ff0ad9b9cdd675ad23a27ddd8c4b684e5f78de68e374ab3ed607f5'
for root,manifest in [(O/'candidate',j(cm)),(O/'fresh-review',j(rm))]:
 for x in manifest['files']:
  p=root/x['path'];assert h(p)==x['raw_sha256'] and p.stat().st_size==x['bytes']
review=j(rm);assert review['verdict']=='POLICY_ACCEPTABLE_FOR_OWNER_ADOPTION'
scope={'scope_id':'B3-V1-CONTINUOUS-POLICY-SUCCESSOR-01-OWNER-ADOPTION.candidate.1','request_status':'PREPARED_NOT_APPROVED','subject':j(cm)['subject'],'candidate_manifest':{'path':str(cm),'raw_sha256':h(cm)},'normative_source':{'path':str(O/'candidate/POLICY_SUCCESSOR.candidate.1.md'),'raw_sha256':h(O/'candidate/POLICY_SUCCESSOR.candidate.1.md')},'supporting_candidate_files':j(cm)['files'],'fresh_review':{'path':str(rm),'raw_sha256':h(rm),'verdict':review['verdict'],'scope':review['scope'],'native_reviewer_profile_qualification':review['native_reviewer_profile_qualification'],'not_native_product_review':True},'proposed_Human_decision':'Accept only the fixed source-bound policy annex interpretation; original mandatory native entry/lifecycle/review/qualification gates prevail','accepted_semantics_if_approved':['F01 only additional source-proven advisory pending observations, conjunctive parked/deadline rules; no mandatory review bypass','F02 bounded exact Owner decision container with distinct original native per-Unit authority; no reusable parent dispatch Grant or unknown future binding approval','F03 candidate-to-candidate implementation remains forbidden; this capability is outside adoption claim'],'no_effects':['No Program/Policy/Controller activation or native evaluator/Schema/source rewrite','No actual Batch members or96 Grants approved','No Product/Candidate Coding/Dispatch/Writer/Qualification authority','No Git Integration/ref/Commit/Push/Merge/main migration','No SQL/Broker/LIVE/Runtime/Restore effects','No acceptance of future Unit results or transfer of U01/U02 receipts'],'materialization_boundary':'Any later receipt/source integration must follow existing exact governance and permitted paths. This request does not silently authorize native policy source edits; unsupported operational route remains HOLD.','preserved_source':{'Architecture':'MA-ARCH-REVIEW-v9-SOURCE-CLOSURE-PAIR01','Accepted_Units':'1/96','C3':'NOT_QUALIFIED','C5':'NOT_AUTHORIZED_NOT_EXECUTED','C6':'PENDING_HUMAN','P00':'0/8'}}
out('POLICY_OWNER_ADOPTION_SCOPE.candidate.json',scope)
sha=h(O/'POLICY_OWNER_ADOPTION_SCOPE.candidate.json')
text=f"""# 唯一下一項政策 Owner 決策請求

狀態：候選，尚未 Human 批准。此請求只處理政策來源採納；MA02資格與Git發布各自獨立。

請決定是否精確採納：
- Subject：{scope['subject']}
- Candidate Manifest SHA256：{h(cm)}
- Owner Adoption Scope ID：{scope['scope_id']}
- Scope raw SHA256：{sha}
- Fresh source-only review：POLICY_ACCEPTABLE_FOR_OWNER_ADOPTION
- Review Manifest raw SHA256：{h(rm)}

批准範圍僅三項：
1. 額外 advisory Review 的固定分類、完整parked條件、較早deadline；原mandatory Gate及native routing優先。
2. 有限、逐項精確的Owner決策容器；每Unit仍獨立native AUTH／WO／Writer／成本／消耗。沒有一般可重用parent Batch Grant，也不批准未知未來內容。
3. 明確維持未審candidate-to-candidate實作禁止。

可回覆：
「核准採納 B3-V1-CONTINUOUS-POLICY-SUCCESSOR-01/candidate.1，僅限 Scope SHA256 {sha} 的三項縮限政策來源；其餘權限保留。」

此回覆不核准任何實際Unit／Batch成員、Coding、候選開發、Qualification、Program/Policy/Controller Activation或Git/SQL/Broker/Runtime。原生policy若仍回pending route，必須HOLD；正式source整合／收據物化仍依既有精確程序，不能靜默修改受保護來源。

其他下一步：
- MA02-U01：已固定source／U01 scoped reuse proof／9 Fixture／WO compilation候選。仍須MA02專用適用性與實際使用資格，之後才有exact Coding Grant決策。
- 文件公開：GIT_PUBLICATION_AUDIT列出全部missing raw hashes及建議獨立分支；先完成新的public allowlist／隱私secret scan與精確scope，再申請新的Git Grant。原v3/NAV不可重用。
- 不需要重開B3或Bridge，不需要新的Controller。
"""
with (O/'NEXT_MINIMUM_HUMAN_DECISION_REQUEST.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
out('NEXT_AUTHORITY_MATRIX.json',{'role':'DERIVED_GATE_PLAN_NOT_GRANT','gates':[{'gate':'Policy annex exact Owner adoption','status':'READY_FOR_HUMAN_SOURCE_ADOPTION_DECISION','evidence':str(O/'POLICY_OWNER_ADOPTION_SCOPE.candidate.json'),'required_authority':'Exact Human decision','does_not_unblock':'Any native mandatory pending route or unit qualification/coding automatically'},{'gate':'MA02 intended-use applicability','status':'NOT_ESTABLISHED_FOR_MA02','evidence':str(O/'MA02_U01_PREPARATION.candidate.json'),'required_authority':'Bounded MA02-specific applicability/source-review decision if no current exact qualified profile; U01/U02 scope nontransferable','does_not_require':'All PK01/P00 closure as blanket rule'},{'gate':'MA02 actual Manual use Qualification','status':'NOT_OBTAINED','required_authority':'Exact trial Grant after applicable route is legally accepted; real required local identity/continuity evidence, not synthetic alone','does_not_require':'Unrelated future Broker/SQL/LM resource qualification'},{'gate':'MA02 Coding Grant','status':'NOT_ELIGIBLE_TO_REQUEST_AS_READY_YET','evidence':str(O/'MA02_U01_WO_COMPILATION_INPUT.candidate.json'),'required_before':'Qualified intended-use Source/Context/Result/Intake/Executor; exact native membership/WO/preimages/budget/source/reuse; fresh single-writer eligibility','required_authority':'New exact Human Coding Grant, not this policy or oldU01 grant'},{'gate':'New documentation publication','status':'AUDIT_COMPLETE_NEW_PUBLICATION_SCOPE_NOT_AUTHORIZED','required_before':'Exact safe public projection/allowlist/raw hashes/base/privacy/secret scan','proposed_branch':'codex/b3-v1-precompiled-policy-handoff-successor-01','proposed_base':'e287f6ac0744875e8d4bca103a6b73b4cf53416d','required_authority':'New exact Git Grant'},{'gate':'Compiler/C3 route','status':'HOLD_NOT_QUALIFIED','required_before':'Actual applicable trusted Host/Injection/Continuity/RQ03/Context evidence and exact Successor policy/grant','no_repeated_resource_question':True},{'gate':'C5/C6/P00','status':'C5 NOT_AUTHORIZED_NOT_EXECUTED; C6 PENDING_HUMAN; P00 0/8','rule':'No blanket rewrite or exemption; exact per-use applicability remains'}]})
out('FINAL_REVIEW_RECEIPT_VERIFICATION.json',{'role':'ROOT_VERIFICATION_OF_INDEPENDENT_OUTPUT_NOT_NEW_VERDICT','candidate_manifest':h(cm),'review_manifest':h(rm),'review_report':h(O/'fresh-review/FRESH_INDEPENDENT_POLICY_REVIEW_REPORT.md'),'all_fixed_members_match':True,'reviewer':'/root/fresh_policy_successor_review','fork_turns':'none','verdict':review['verdict'],'scope':review['scope'],'remaining_policy_semantic_findings':0,'native_Reviewer_qualification':'NOT_ESTABLISHED; not a controlled product Review receipt','policy_adoption':False})
print(json.dumps({'Owner_scope_SHA256':sha,'review_verified':True,'verdict':review['verdict']}))

