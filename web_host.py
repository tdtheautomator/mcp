import gradio as gr
from llm_agent import connect_mcp, get_response, check_tool


initialize = False
messages = None
tool_messages = None


async def load():
    global initialize, tool_messages, messages
    if initialize is not True:
        initialize = True
        tool_messages = await connect_mcp()


async def chat(message, history, v):

    if len(history) == 0 and messages != None:
        for content in messages:
            history.append(content)

    chat_messages = []
    for content in history:
        chat_messages.append(content)
    chat_messages.append({
        "role": "user",
        "content": "user question: "+message
    })

    md = None
    api_request_content = get_response(chat_messages).choices[0].message.content
    if await check_tool(api_request_content, chat_messages):
        assistant_output = get_response(chat_messages).choices[0].message.content
        md = gr.Markdown(value=(v+"   \n"+api_request_content))
    else:
        assistant_output = api_request_content

    return assistant_output, md


with gr.Blocks() as demo:
    def on_check(f):
        global messages
        if f:
            messages = tool_messages
        else:
            messages = None

    demo.load(load, inputs=[])
    code = gr.Markdown(render=False)
    check = gr.Checkbox(render=False, label="enable mcp servers")
    with gr.Row():
        check.render()
    with gr.Row():
        with gr.Column():
            gr.ChatInterface(
                chat,
                additional_inputs=[code],
                additional_outputs=[code],
                type="messages"
            )
    check.change(on_check, inputs=[check])

demo.launch()