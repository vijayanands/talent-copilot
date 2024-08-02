from helpers.confluence import clean_confluence_content

# Example usage
confluence_html = """
<div class="confluence-content">
    <h1>Welcome to Confluence</h1>
    <p>This is a <strong>sample</strong> Confluence page.</p>
    <div class="code-block">
        <pre><code>print("Hello, Confluence!")</code></pre>
    </div>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    <!-- This is a comment that should be removed -->
    <script>
        // This script should be removed
        console.log("This should not appear in the output");
    </script>
</div>
"""

clean_content = clean_confluence_content(confluence_html)
print(clean_content)
