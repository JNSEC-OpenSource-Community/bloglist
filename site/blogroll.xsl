<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes" doctype-system="about:legacy-compat" />

  <xsl:template match="/">
    <html lang="zh-CN">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="{blogroll/description}" />
        <title><xsl:value-of select="blogroll/title" /></title>
        <link rel="stylesheet" href="style.css" />
      </head>
      <body>
        <main class="page-container">
          <section class="masthead">
            <p class="overline">JNSEC OPEN SOURCE COMMUNITY</p>
            <h1>Blogs</h1>
            <p class="description"><xsl:value-of select="blogroll/description" /></p>
            <nav class="utility-links" aria-label="页面链接">
              <a href="opml.xml" download="opml.xml">OPML</a>
              <xsl:if test="string-length(normalize-space(blogroll/repository)) &gt; 0">
                <a href="{blogroll/repository}" target="_blank" rel="noreferrer">GitHub</a>
              </xsl:if>
            </nav>
          </section>

          <section class="about" aria-labelledby="about-heading">
            <h2 id="about-heading">About feeds</h2>
            <p>Feed 是网站公开发布的一份更新清单。博客把文章的标题、链接、发布时间和摘要写入 XML，RSS 阅读器定期读取它们，再把多个网站的更新集中在一起。</p>
            <p>RSS 0.90 由 Netscape 在 1999 年发布，之后出现了 RSS 0.91、RSS 1.0 和 RSS 2.0 等发展路线；Atom 是另一种常见的订阅格式。虽然名称和结构不同，它们解决的都是同一个问题：让读者订阅网站，而不必反复访问每个主页。</p>
            <p>这里的每个博客都可能提供一个 Feed。<code>OPML</code> 文件则是一份订阅源清单，可以一次性导入阅读器；如果只想订阅某一个博客，也可以直接使用条目后的 Feedly、Inoreader 或 Folo 链接。</p>
            <p>本页的原始数据是 XML。XML 顶部的 <code>xml-stylesheet</code> 声明告诉浏览器使用 XSLT；XSLT 再通过模板和 XPath 将数据转换为 HTML，因此内容和页面样式可以分开维护。</p>
            <p class="about-links">
              <a href="https://taxodium.ink/about-feeds.html" target="_blank" rel="noreferrer">关于订阅源</a> ·
              <a href="https://www.rssboard.org/rss-history" target="_blank" rel="noreferrer">RSS 历史</a> ·
              <a href="https://www.ibm.com/docs/zh/i/7.5.0?topic=functions-transforming-xslt-stylesheets" target="_blank" rel="noreferrer">IBM：使用 XSLT 变换 XML</a>
            </p>
          </section>

          <section class="blog-section" aria-labelledby="blog-heading">
            <h2 id="blog-heading" class="list-heading">Blogs</h2>
            <div class="blog-list">
              <xsl:choose>
                <xsl:when test="count(blogroll/blogs/blog) &gt; 0">
                  <xsl:for-each select="blogroll/blogs/blog">
                    <article class="blog-entry">
                      <div class="entry-body">
                        <h3><a href="{@homepage}" target="_blank" rel="noreferrer"><xsl:value-of select="@name" /></a></h3>
                        <xsl:if test="string-length(normalize-space(description)) &gt; 0">
                          <p class="entry-description"><xsl:value-of select="description" /></p>
                        </xsl:if>
                        <p class="entry-links">
                          <a href="{@homepage}" target="_blank" rel="noreferrer">主页</a>
                          <xsl:if test="string-length(normalize-space(@feed)) &gt; 0">
                            <span aria-hidden="true"> · </span>
                            <a href="{@feed}" target="_blank" rel="noreferrer">Feed</a>
                            <span aria-hidden="true"> · </span>
                            <a class="reader-link" data-reader="folo" data-feed="{@feed}" href="{@feed}" target="_blank" rel="noreferrer">Folo</a>
                            <span aria-hidden="true"> · </span>
                            <a class="reader-link" data-reader="feedly" data-feed="{@feed}" href="{@feed}" target="_blank" rel="noreferrer">Feedly</a>
                            <span aria-hidden="true"> · </span>
                            <a class="reader-link" data-reader="inoreader" data-feed="{@feed}" href="{@feed}" target="_blank" rel="noreferrer">Inoreader</a>
                          </xsl:if>
                          <xsl:for-each select="tags/tag">
                            <span class="tag">#<xsl:value-of select="." /></span>
                          </xsl:for-each>
                        </p>
                      </div>
                    </article>
                  </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                  <p class="empty-state">暂无博客条目。</p>
                </xsl:otherwise>
              </xsl:choose>
            </div>
          </section>
        </main>

        <script type="text/javascript"><![CDATA[
          (function () {
            document.querySelectorAll('[data-reader][data-feed]').forEach(function (link) {
              var feed = encodeURIComponent(link.getAttribute('data-feed'));
              var urls = {
                folo: 'https://app.folo.is/discover?keyword=' + feed,
                feedly: 'https://feedly.com/i/subscription/feed/' + feed,
                inoreader: 'https://www.inoreader.com/feed/' + feed
              };
              var reader = link.getAttribute('data-reader');
              if (urls[reader]) link.href = urls[reader];
            });
          }());
        ]]></script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
