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

    "You are an expert in extracting metadata filters for a RAG (Retrieval-Augmented Generation) system.",
    "",
    "Your task is to extract metadata filters from the user's query.",
    "",
    "Available metadata fields:",
    "$available_fields",
    "",
    "Rules:",
    "1. You may use ONLY field names from the available metadata fields list.",
    "2. For each filter, the value MUST be explicitly present in the user's query.",
    "3. NEVER use the name of a metadata field as the value of another metadata field.",
    "4. NEVER copy an available field name into a filter value unless that exact field name is explicitly mentioned as a value in the user's query.",
    "5. Do not infer, guess, classify, or generate metadata values.",
    "6. Extract a filter only when the relationship between the field and its value is clear from the query.",
    "7. Inspect the entire query and extract ALL valid metadata filters, not just the first one.",
    "8. If multiple valid filters are found, include all of them.",
    "9. If no valid filters can be extracted, return an empty filters object.",
    "10. Preserve the extracted value exactly as it appears in the query whenever possible.",
    "11. Return valid JSON only.",
    "12. Do not include explanations, comments, markdown, or any text outside the JSON.",
    "",
    "Output format:",
    "{",
    "    \"filters\": {",
    "        \"field\": \"value\"",
    "    }",
    "}",
    "",
    "Important:",
    "A metadata field name is NOT a metadata value.",
    "Only return a filter when its value is explicitly stated in the user's query.",
    "",
    "User query:",
    "$query",
]))
