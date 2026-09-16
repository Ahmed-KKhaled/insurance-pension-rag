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

