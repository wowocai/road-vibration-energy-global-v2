# Upload-ready layout

## GitHub
Extract GitHub_code.zip into the repository working tree. It contains source, documentation and environment files. Do not commit the large data archive into normal Git history. The .gitignore excludes large generated inputs and outputs.

## Zenodo
Upload Zenodo_data.zip together with the code-release archive (or link the corresponding GitHub release using Zenodo's GitHub integration). The two archives share the same root folder and are designed to merge after extraction. SHA256SUMS.txt records the combined release tree. Optionally use the all-in-one archive as a single review download.

Fill in the verified paper title, authors, affiliations, version, license and related identifiers in Zenodo. No author list or DOI is invented in this preparation. After publishing, insert the actual Zenodo record URL/DOI in the GitHub README and manuscript Data/Code availability statements, and link the repository release back to that record. The GitHub URL supplied by the author could not be fetched in this session, so existing remote contents were not merged or overwritten.

Suggested Chinese availability statement after publication: “代码与处理后数据公开于[仓库URL]及其关联的Zenodo数据记录[实际DOI]，包含环境配置、依赖版本和脚本级工作流程说明。”
