# JNSEC OpenSource Community Blog List

JNSEC-OSC 朋友们的博客

## 添加一条博客

在 `data/blogs.json` 的 `blogs` 数组最后添加：

```json
{
  "name": "你的名字的博客",
  "homepage": "https://example.com/",
  "feed": "https://example.com/feed.xml",
  "description": "简单介绍你的博客会分享什么内容。",
  "tags": ["编程"]
}
```

字段说明：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `name` | 是 | 博客显示名称 |
| `homepage` | 是 | 博客主页，必须是完整的 `http://` 或 `https://` 地址 |
| `feed` | 否 | RSS 或 Atom 地址；没有时填写空字符串 `""` |
| `description` | 否 | 一句话介绍 |
| `tags` | 否 | 标签数组，例如 `["编程", "Linux"]` |

### JSON 初学者注意事项

- 只能使用英文双引号 `"`，不能使用中文引号。
- 同一个数组中的两条记录之间需要逗号，最后一条后面不要加逗号。
- JSON 不支持注释；不要在文件里写 `// ...`。
- 不要删除其他人的条目。
- 按文件现有顺序，把新博客放在 `blogs` 数组最后。
- 没有 RSS 不代表不能添加博客，把 `feed` 留空即可。

## 不使用命令行也可以贡献

1. 打开 `data/blogs.json`。
2. 点击 GitHub 页面右上角的铅笔按钮（Edit this file）。
3. 在 `blogs` 数组末尾复制一条已有记录，替换为自己的信息。
4. 在页面底部选择 **Create a new branch and start a pull request**。
5. 创建 Pull Request，并等待自动检查。
6. 如果检查失败，打开检查详情，根据错误提示修改 JSON；不确定时可以在 PR 中提问。

## GitHub Pages

工作流位于 `.github/workflows/pages.yml`。仓库管理员只需在 **Settings → Pages** 中将发布来源设为 **GitHub Actions**；默认分支更新后，网站会自动构建并发布。

本地检查：

```bash
python scripts/build.py --check
python -m http.server 8000 --directory site
```

然后打开 <http://localhost:8000/>。
