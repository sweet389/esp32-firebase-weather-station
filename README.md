# Estacao meteorológica utilizando um esp32 + firebase

Neste projeto e utilizado um sensor de pressao e temperatura (bmp280), em que um Esp32 pega os dados e envia eles para o servidor que pode ser um PC por exemplo, via socket

Nisso o PC pega esses dados, os trata e adiciona a data em que foi recebido, nisso, pelo protocolo HTTP usando a lib requests, podemos fazer a integracao ao firebase, que envia os dados ao Realtime Database por HTTP,
tendo tambem a possibilidade de puxar eles pelo HTTP usando GET, assim podendo ser usado nao so em outros projetos mas tambem acessado de qualquer lugar.
