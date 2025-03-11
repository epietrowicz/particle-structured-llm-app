import json
import serial

from ollama import chat
from ollama import ChatResponse
from faster_whisper import WhisperModel

model_size = "tiny.en"
test_file = "too-cold-in-here.mp3"
current_state = {"lights": 50, "window": 20, "temperature": 30, "fan": 0}


def transcribe_audio():
    # Run on GPU with FP16
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(test_file, beam_size=5)
    segments = list(segments)

    for segment in segments:
        print("Transcription: '%s'" % segment.text)

    return segments[0]


def format_prompt(segment):
    prompt = f"""Update the state based on the given text. Return the new state in JSON format. 
    Always include a complete state, even if the key does not require an update. The values represent 0 to 100 percent.
    A request to change a value should be followed by the new value.
    The keys are:
    - lights
    - window
    - temperature
    - fan

    The current state:
    {current_state}

    Text: "{segment.text}"
    """

    return prompt


def parse_response(response):
    global current_state

    response_str = response["message"]["content"]
    json_str = response_str.split("```json")[1].split("```")[0]
    json_str = json_str.replace("'", '"')

    new_state = json.loads(json_str)
    print(f"Current state: {current_state}")
    print(f"New state: {new_state}")
    current_state = new_state

    return json_str


def write_to_serial(json_str):
    try:
        ser = serial.Serial("/dev/ttyACM0", 9600)
        ser.write(json_str.encode())
        ser.close()
    except serial.SerialException:
        print("Could not write to serial port.")


def main():
    audio_segment = transcribe_audio()
    prompt = format_prompt(audio_segment)

    response: ChatResponse = chat(
        model="gemma2:2b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    json_str = parse_response(response)
    write_to_serial(json_str)


main()
