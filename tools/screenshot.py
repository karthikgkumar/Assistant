from pydantic import BaseModel, Field
from typing import Optional, Type
from agent.agent import AvaAgent
# Set up your language model
llm = OpenaiLLM(
) 

class ScreenshotArgs(BaseModel):
    action: str = Field(
        description="The action to perform: 'take_screenshot'.",
        example="take_screenshot"
    )
    filename: str = Field(
        description="The filename to save the screenshot as (e.g., 'screenshot' or 'screenshot.png'). If no extension is provided, '.png' will be used.",
        default=None
    )

class ScreenshotTool(BaseTool):
    name: str = "screenshot"
    description: str = "Take a screenshot of the entire screen or a specific region"
    args_schema: Optional[Type[BaseModel]] = ScreenshotArgs
    return_direct: Optional[bool] = False

    def _run(self, action: str, filename: Optional[str] = None) -> str:
        from PIL import ImageGrab
        import win32clipboard
        import io
        import pyautogui
        import threading
        import os
        

        def copy_image_to_clipboard(image):
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        if action == "take_screenshot":
            pyautogui.hotkey('alt', 'a')  # Press ALT + A
            if filename is None:
                filename = f"screenshot_{threading.get_ident()}.png"
            else:
                if not filename.endswith('.png'):
                    filename += '.png'

            pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")
            screenshots_folder = os.path.join(pictures_folder, "Screenshots")
            screenshot_path = os.path.join(screenshots_folder, filename)
            os.makedirs(screenshots_folder, exist_ok=True)
            image = ImageGrab.grab()
            image.save(screenshot_path)
            copy_image_to_clipboard(image)
            pyautogui.hotkey('alt', 'a')
            return f"Screenshot saved as {filename} and copied to clipboard"
        else:
            return "Error: Invalid action specified."
sys_prompt = """You are a helpful assistant that can take screenshots on the local system. 
The user may ask you to take a screenshot and optionally provide a filename to save it as."""

tools = [ScreenshotTool()]

agent = AvaAgent(
    sys_prompt=sys_prompt,
    ava_llm=llm,
    tools_list=tools,
    logging=True,
    use_system_prompt_as_context=True,
    pickup_mes_count=6
)

while True:
    user_input = input("Human: ")
    if user_input.lower() == "exit":
        break
    response = agent.run(user_input)
    print("Agent:", response)
