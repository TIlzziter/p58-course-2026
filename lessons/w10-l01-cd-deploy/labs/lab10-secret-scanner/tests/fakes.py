"""Ненастоящие секреты для тестов. Собираем их из кусков, чтобы сами тесты не выглядели как утечка
(GitHub push protection и другие сканеры ищут такие строки целиком)."""
TG = "123456789" + ":" + "AAH" + "x7Kq2LmN9pRt4VwZ8bC1dE5fG3hJ6kM0"   # 9 цифр : 35 символов
GH = "gh" + "p_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"            # gh?_ + 36 символов
AWS = "AK" + "IA" + "QWERTY7UIOP2ASDF"                                  # AKIA + 16
PEM = "-----BEGIN " + "RSA PRIVATE KEY-----"
assert len(TG.split(":")[1]) == 35 and len(GH) == 40 and len(AWS) == 20
