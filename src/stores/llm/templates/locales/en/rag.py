from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template("\n".join([
    "You are an assistant to generate a response for the user.",
    "You will be provided by a set of docuemnts associated with the user's query.",
    "You have to generate a response based on the documents provided.",
    "Ignore the documents that are not relevant to the user's query.",
    "You can apologize to the user if you are not able to generate a response.",
    "You have to generate response in the same language as the user's query.",
    "Be polite and respectful to the user.",
    "Be precise and concise in your response. Avoid unnecessary information.",
]))

#### Document ####
document_prompt = Template(
    "\n".join([
        "## Document No: $doc_num",
        "### Content: $chunk_text",
    ])
)

#### Footer ####
footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the user.",
    "## Question:",
    "$query",
    "",
    "## Answer:",
]))


query_rewriter_prompt = Template("\n".join([
    "Rewrite the user's latest question into a standalone and clear search query.",
    "",
    "Use the conversation history to resolve references and pronouns such as:",
    "- he",
    "- she",
    "- it",
    "- this",
    "- that",
    "- them",
    "- the previous one",
    "- the next one",
    "- the one mentioned earlier",
    "",
    "Rules:",
    "- Preserve the original meaning of the question.",
    "- Do not answer the question.",
    "- Return only the rewritten search query.",
    "- If the question is already standalone and clear, return it unchanged.",
    "- Write the rewritten query in English.",
    "",
    "Conversation history:",
    "$chat_history",
    "",
    "Latest user question:",
    "$query",
    "",
    "Standalone search query:",
]))


vision_table_extractor_prompt = Template("\n".join([

    "Extract the text contained in the table shown in the image.",

    "",

    "Rules:",

    "- Extract all text contained in the table.",
    "- Do not summarize the content.",
    "- Do not answer any question.",
    "- Do not add any information that is not present in the image.",
    "- Do not invent or infer text that is unclear in the image.",
    "- Preserve words and numbers as they appear in the image.",
    "- Preserve the order of rows and columns.",
    "- If a cell contains multiple lines, combine them into a single text.",
    "- Return clear text suitable for use in a RAG pipeline.",

    "",

    "Extracted table text:",

]))


metadata_filter_extractor_prompt = Template("\n".join([

    "You are an expert in extracting metadata filters for a RAG system.",
    "",
    "Your task is to extract metadata filters that can be explicitly identified from the user's query.",
    "",
    "Available metadata fields:",
    "$available_fields",
    "",
    "Rules:",
    "1. Use only field names that exist in the available metadata fields.",
    "2. Extract a filter only when its value is explicitly mentioned in the user's query.",
    "3. The relationship between the field and its value must be clear from the user's query.",
    "4. Do not infer, guess, or assume any value based on the meaning or context of the query.",
    "5. Do not assume a default value for any field that is not mentioned in the query.",
    "6. Do not use external knowledge to determine the value of any field.",
    "7. Do not use a metadata field name as the value of another metadata field.",
    "8. Do not return values such as \"unknown\", \"undefined\", \"not specified\", or null when a field value is not explicitly mentioned.",
    "9. If the user does not provide a value for a field, do not include that field in the filters.",
    "10. Examine the entire query and extract all valid metadata filters.",
    "11. If multiple valid filters are present, return all of them.",
    "12. Preserve filter values as they appear in the user's query whenever possible.",
    "13. Do not reinterpret or rewrite a filter value unless necessary to preserve its meaning.",
    "14. If no valid metadata filter can be extracted, return an empty filters object.",
    "15. Return valid JSON only.",
    "16. Do not include explanations, comments, Markdown, or any text outside the JSON object.",
    "",
    "IMPORTANT:",
    "The presence of a metadata field in the available fields does not mean that the field must appear in the output.",
    "Include a field only when a clear and explicit value for that field exists in the user's query.",
    "If a field has no explicit value in the query, ignore that field instead of creating a value for it.",
    "",
    "Generic example:",
    "",
    "Available metadata fields:",
    "[\"field_a\", \"field_b\", \"field_c\"]",
    "",
    "User query:",
    "\"A question containing an explicit value for field_a\"",
    "",
    "Output:",
    "{",
    "    \"filters\": {",
    "        \"field_a\": \"explicit value\"",
    "    }",
    "}",
    "",
    "If the query contains no value that can be clearly associated with any available metadata field:",
    "{",
    "    \"filters\": {}",
    "}",
    "",
    "Output format:",
    "{",
    "    \"filters\": {",
    "        \"field\": \"value\"",
    "    }",
    "}",
    "",
    "User query:",
    "$query",
]))
