# B3 V1 已採納架構：公開承載 v3 候選

此目錄是固定架構及工程候選的閱讀入口，尚無 Git Publication Grant，也不是第二套 Current 或 Controller。

先讀 docs/architecture/B3_V1_ARCHITECTURE.md、docs/PROJECT_OPERATING_GUIDE.md 與本目錄 READABLE_CONTRACT_INDEX.v3.json。工程入口為 engineering/12_PACKAGE_ENGINEERING_SPECIFICATION_INDEX.json；95 API及96 Units的規範欄位沿用原固定來源，不因投影取得施工資格。

43 份 derived/pairs/<operation>.json 提供全部 4,372 Pair 的逐項可讀查詢投影；原109,905,310-byte canonical JSON完整保留於 gzip carrier，解壓後必須核對原raw SHA256。Projection不是 canonical，不重新產生Identity、Acceptance或新版Schema。24份carrier的原raw hash與壓縮storage hash分開。

18份原私人研究／Owner／Review正文保留於私人原工作區，本公開候選不納入其bytes，以 exact SHA256 descriptor辨識。其缺失不能假稱已讀回，也不能被摘要代替。合成測試資料夾名稱private不等於真實私人歷史；其選取仍須Human對精確bytes批准。

Publication與C3獨立。C3 Attempt01實際NOT_QUALIFIED；C5未授權／未執行，C6待Human，P00仍0/8。實際Current優先讀repository docs/CURRENT_STATE.md，若舊投影與後續固定證據不一致，STOP受影響狀態轉移並使用精確補充證據，不自行修復權威。

此 v3 僅為新 Public Scope／Representation／Git Effects 決策候選。舊 v2 scope、adopted canonical bytes、Receipt和已接受歷史不被修改。
