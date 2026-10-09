# R06 SOURCE01 五檔 compatibility 與 compact-current 保全候選

Input `bae9dcaff476bd79e8494ac6cd393dea19cb9657`，authoritative master `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`。候選 canonical SHA256 `5f795b360ad84d1e116cdf47f91c829f951ddebfe711eb84807349251dc51a52`；combined zero-context patch `a70cbd717da426e0c086c6c35da8a4879a45fb4b6bac38239923067907da0457`。未套用原 repository，未授權 migration、publication 或 P01/P02 product implementation。

## 精確範圍與新發現

| 檔案 | 候選責任 |
|---|---|
| scripts/p00_context.py | 同原三個 hunks，negative active/hash/path/mandatory/source-baseline drift保全 |
| scripts/p00_reading_eval.py | 原runner也固定要求missing-negative；必須新增represented-but-not-qualified分支，拒絕unknown或source/hash/semantic/intake矛盾 |
| tests/platform/test_p00_context.py | active negative shared fixture＋missing/inactive/hash/unsafe/drift/alias/dirty反例 |
| tests/platform/test_p00_reading.py | negative mandatory obligation與完整source representation；閱讀/intake仍false |
| tests/platform/test_p00_reading_eval.py | exact current測試HEAD successor；舊36f6c07只作historical source，changed loaded owner明確拒絕，不靜默重綁 |

原compiler／packer／reading owner、policies、CURRENT、contracts、packages、過去reports／subject未改。Future5檔before Git blobs/rawSHA256與proposed afterSHA256完整列於JSON；不是以「P00檔案」授權。Existing runner legacy gap row保留原id/outcome，successor新增獨立representation row；全部output仍NOT_QUALIFIED，原aggregate gate不放寬。歷史full report重現需exact old owners，不把新HEAD當舊report subject。

## 隔離驗證與限制

107 passed /207.73s，涵蓋context、compiler、context_pack、reading、reading_eval五份測試；只在ignored Git fixture `3af98b884e79581d3ab89811a8922038c5ec573b`，parent為input。Fixture讀取original objects作readonly alternates，只寫新temporary objects/index/refs與精確docs/platform/test檔案，不checkout產品或data。此commit不是execution ID、accepted source subject、registry、receipt或publication payload。

先前alternates CRLF與缺少pytest basetemp parent均為fixture setup問題：第一pytest69passed/38setup errors並非PASS；修正LF／.tmp parent後新fixture107passed，候選owner patch未因錯誤更改。仍須完整migrated platform／package compatibility與獨立審查，再取得exact migration authority；本輪原repo regression另記validation。

## CURRENT逐byte保全與context

兩份原始CURRENT共148,689 bytes：完整current前段5,910，history142,779；14個current全文閱讀block與8個contiguous raw-byte segments逐字保留，全部bytes可重建，6個history chunks有exact range/hash/full-source load義務。七個active policy refs仍必須完整讀取，negative source1,496 bytes完全納入非authority projection；13denied/7invariants不裁切。任何historical／contradiction／review／provenance／未分類語意都必須載入原source。

Projection carrier10,946 bytes只是未審候選，不能取代原mandatory gate或current pointers。即使診斷上物理精簡全部CURRENT history，P01/P02 mandatory仍782,400／733,725 bytes（尚未加入projection metadata），仍超131,072。Existing packer早已分隔history，因此不把同一分段重複當成新pack節省。原policy／compiler／P01-r5／P02-r2 unchanged，gate NOT_PASSED。

## 必要決策、風險與下一步

SOURCE01 still requires independent compatibility／semantic review and exact adoption grant；SOURCE02 CSV A/B未選定。Seven intake UNKNOWN和兩類來源投影NONE不可轉成global completeness，producer／model reading／STOP-CAS-backend尚未qualified。下一步合法authoring是完整context剩餘大型carrier的preservation與representation boundary，不能只重複CURRENT-only精簡或刪除negative/safety。

LOCAL_COMMITTED candidate／REMOTE current-turn NOT_PUBLISHED／REVIEW_PENDING prepared only／P00 NOT_ACCEPTED／product NOT_AUTHORIZED。P00完整結案0/8、journeys0/6、product completion UNCALIBRATED。Exact manifest須final payload freeze後另建repository外，舊bae9dcaf核准提案不包括新commits。

## References／可重現性

同名compatibility-candidate JSON包含34原始source refs、五檔before/after與trial scope；combined patch只作check。compatibility-reproduce.py產生新的ignored fixture，compact-current.reproduce.py只輸出JSON，mapping／projection與source ranges可獨立重建。所有流程不建立operational truth或授權。

Additional preservation proof: candidate evaluator and original owner give byte-identical canonical pure legacy outputs for both exact36f6c07 context inputs,20 cases each. This comparison is not full bound report replay/qualification. Complete compact mapping JSON reproduced identically; current intake remains7 UNKNOWN/2 source-only NONE, no trusted producer/registry.
