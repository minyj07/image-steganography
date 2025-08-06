# -*- coding: utf-8 -*-
import argparse
from PIL import Image

# 메시지의 끝을 알리는 고유 구분자 (32비트)
# 16개의 1과 16개의 0으로 구성하여, 일반적인 데이터와 겹칠 확률을 최소화합니다.
DELIMITER = "11111111111111110000000000000000"

def text_to_binary(text):
    """
    문자열을 2진수 비트 스트림으로 변환합니다.
    각 문자는 UTF-8로 인코딩된 후 8비트 2진수로 표현됩니다.
    """
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binary_to_text(binary_data):
    """
    2진수 비트 스트림을 다시 문자열로 변환합니다.
    8비트씩 묶어 문자로 디코딩합니다.
    """
    # 8비트 배수가 아닌 경우, 패딩된 비트를 제거합니다.
    binary_data = binary_data[:len(binary_data) - (len(binary_data) % 8)]
    
    byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    text = bytearray()
    for byte in byte_data:
        text.append(int(byte, 2))
    
    try:
        return text.decode('utf-8')
    except UnicodeDecodeError:
        return "오류: 숨겨진 데이터를 UTF-8로 디코딩할 수 없습니다."


def hide_message(input_path, output_path, message):
    """
    이미지 파일에 비밀 메시지를 숨깁니다. (LSB 기법 사용)
    웹 앱에서 사용하기 위해 결과를 반환하도록 수정되었습니다.
    """
    try:
        image = Image.open(input_path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError(f"오류: 입력 파일 '{input_path}'를 찾을 수 없습니다.")

    # 메시지를 2진수로 변환하고, 끝에 구분자를 추가합니다.
    binary_message = text_to_binary(message) + DELIMITER
    
    # 이미지가 메시지를 숨길 만큼 충분한 공간을 가졌는지 확인합니다.
    max_bytes = (image.width * image.height * 3)
    if len(binary_message) > max_bytes:
        raise ValueError(f"오류: 메시지가 너무 깁니다. 이 이미지에는 최대 {max_bytes // 8} 바이트까지 숨길 수 있습니다.")

    new_image = image.copy()
    pixels = new_image.load()
    data_index = 0
    
    # 이미지의 각 픽셀을 순회합니다.
    for y in range(image.height):
        for x in range(image.width):
            pixel = list(pixels[x, y])
            for i in range(3): # R, G, B
                if data_index < len(binary_message):
                    pixel[i] &= 254
                    pixel[i] |= int(binary_message[data_index])
                    data_index += 1
            pixels[x, y] = tuple(pixel)
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break
    
    new_image.save(output_path, 'PNG')
    return True


def extract_message(input_path):
    """
    이미지 파일에서 비밀 메시지를 추출합니다.
    웹 앱에서 사용하기 위해 결과를 반환하도록 수정되었습니다.
    """
    try:
        image = Image.open(input_path, 'r')
    except FileNotFoundError:
        raise FileNotFoundError(f"오류: 입력 파일 '{input_path}'를 찾을 수 없습니다.")

    pixels = image.load()
    binary_data = ""
    
    # 이미지의 각 픽셀을 순회하며 LSB를 추출합니다.
    for y in range(image.height):
        for x in range(image.width):
            pixel = pixels[x, y]
            for i in range(3): # R, G, B
                binary_data += str(pixel[i] & 1)
                if len(binary_data) >= len(DELIMITER) and binary_data.endswith(DELIMITER):
                    secret_data = binary_data[:-len(DELIMITER)]
                    return binary_to_text(secret_data)

    return "오류: 이미지에서 메시지 끝을 알리는 구분자를 찾지 못했습니다."


def main():
    # 커맨드라인 인터페이스 설정
    parser = argparse.ArgumentParser(description="이미지 스테가노그래피 도구: 이미지 속에 비밀 메시지를 숨기거나 추출합니다.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='실행할 명령어')

    # 'hide' 명령어 설정
    hide_parser = subparsers.add_parser('hide', help='이미지에 메시지를 숨깁니다.')
    hide_parser.add_argument('--input', '-i', type=str, required=True, help='원본 이미지 파일 경로')
    hide_parser.add_argument('--output', '-o', type=str, required=True, help='결과 이미지 파일 경로')
    hide_parser.add_argument('--message', '-m', type=str, required=True, help='숨길 비밀 메시지')
    hide_parser.set_defaults(func=lambda args: hide_message(args.input, args.output, args.message))

    # 'extract' 명령어 설정
    extract_parser = subparsers.add_parser('extract', help='이미지에서 메시지를 추출합니다.')
    extract_parser.add_argument('--input', '-i', type=str, required=True, help='메시지가 숨겨진 이미지 파일 경로')
    extract_parser.set_defaults(func=lambda args: extract_message(args.input))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
