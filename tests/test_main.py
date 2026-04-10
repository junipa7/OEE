import unittest
from auto_st.main import main_function  # main_function은 main.py에서 테스트할 함수입니다.

class TestMain(unittest.TestCase):

    def test_main_function(self):
        # 테스트할 입력값과 예상 결과를 정의합니다.
        input_value = "test input"
        expected_output = "expected output"  # 예상 결과를 정의합니다.
        
        # main_function을 호출하고 결과를 확인합니다.
        result = main_function(input_value)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()