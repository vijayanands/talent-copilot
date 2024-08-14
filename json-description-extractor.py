def extract_description_content(description):
    extracted_content = []
    indent_level = 0
    in_bullet_list = False

    def process_content(content):
        nonlocal indent_level, in_bullet_list
        for item in content:
            if item["type"] == "text":
                text = item["text"]
                marks = item.get("marks", [])
                is_bold = any(mark["type"] == "strong" for mark in marks)
                is_italic = any(mark["type"] == "em" for mark in marks)
                
                if is_bold and is_italic:
                    text = text.upper()
                elif is_bold:
                    text = text.upper()
                elif is_italic:
                    text = text.capitalize()
                
                if in_bullet_list:
                    extracted_content[-1] += text
                else:
                    extracted_content.append("    " * indent_level + text)
            
            elif item["type"] == "paragraph":
                if extracted_content and not in_bullet_list:
                    extracted_content.append("")
                process_content(item["content"])
                if not in_bullet_list:
                    extracted_content.append("")
            
            elif item["type"] == "bulletList":
                in_bullet_list = True
                indent_level += 1
                for list_item in item["content"]:
                    extracted_content.append("    " * (indent_level - 1) + "- ")
                    process_content(list_item["content"])
                indent_level -= 1
                in_bullet_list = False
                extracted_content.append("")
            
            elif item["type"] == "listItem":
                process_content(item["content"])
            
            elif item["type"] == "inlineCard":
                url = item['attrs']['url']
                extracted_content.append(f"    " * indent_level + f"Link: {url}")

    for item in description:
        process_content([item])

    return "\n".join(extracted_content).strip()

# Example usage with a list of dictionaries:
description_list = [
    {
        "type": "paragraph",
        "content": [
            {
                "type": "text",
                "text": "To delete this Sample Project ",
                "marks": [
                    {
                        "type": "strong"
                    }
                ]
            },
            {
                "type": "text",
                "text": "(must be performed by a user with Administration rights)",
                "marks": [
                    {
                        "type": "em"
                    },
                    {
                        "type": "strong"
                    }
                ]
            },
            {
                "type": "text",
                "text": " "
            }
        ]
    },
    {
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Open the administration interface to the projects page by using the keyboard shortcut 'g' then 'g' and typing 'Projects' in to the search dialog"
                            }
                        ]
                    }
                ]
            },
            {
                "type": "listItem",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Select the \"Delete\" link for the \"Sample Scrum Project\" project"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    {
        "type": "paragraph",
        "content": [
            {
                "type": "inlineCard",
                "attrs": {
                    "url": "https://vijayanands.atlassian.net/browse/SSP-17"
                }
            },
            {
                "type": "text",
                "text": " "
            }
        ]
    }
]

print(extract_description_content(description_list))
