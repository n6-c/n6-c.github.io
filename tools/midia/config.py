# Mídia: who sells, and what they share. python3 tools/midia/build.py regenerates every folder.
# Phones are digits only, with country and area code (55 11 9xxxx-xxxx -> "5511927666162").

SELLERS = [
    dict(slug='anderson', name='Anderson Silva', first='Anderson', role='Fundador', phone='5511927666162'),
]

# The commissioned sales partner. Fill the phone (and the name) and rebuild: his card goes live and his folder is generated.
# While PARTNER_PHONE is empty the hub shows a "pasta em preparação" card and no pieces are made.
PARTNER_PHONE = ''
PARTNER_NAME = ''          # e.g. 'João Pereira'; the first word is used for "Fale com João"
PARTNER_ROLE = 'Parceiro comercial'


# ---------------------------------------------------------------- campaigns
# layout: photo | sheet | seq | type | compare | chat | summary | phone
# Every piece is rendered twice: 9:16 (status and stories) and 4:5 (feed).

FICTIONAL_TOWER = 'Estudo fictício feito pela N6C para demonstração.'
FICTIONAL_LOTS = 'Vale do Araçá é um loteamento fictício, criado pela N6C para demonstração.'

CAMPAIGNS = [
    dict(id='obra', title='Do terreno à entrega', who='Construtoras e incorporadoras',
         about='O prédio modelado em 3D do terreno à entrega, com as pranchas técnicas saindo do mesmo modelo. Para lançamento, investidor e comprador.',
         caption=('Olha esse estudo da N6C: o prédio inteiro modelado em 3D, do terreno à entrega, e as pranchas técnicas saem do mesmo modelo das imagens. '
                  'Serve para lançamento, para apresentar ao investidor e para o comprador entender a obra. O filme completo está em n6c.org. '
                  'Quer ver como ficaria com o seu projeto?'),
         pieces=[
             dict(layout='photo', img='entrega.jpg', pos='52% 40%', kicker='Imagens de lançamento',
                  head='O prédio pronto antes da primeira estaca.', line='As imagens e o filme da obra, feitos a partir do seu\u00a0projeto.', note=FICTIONAL_TOWER),
             dict(layout='photo', img='obra.jpg', pos='54% 45%', kicker='Filme da obra',
                  head='A obra inteira, pavimento\u00a0por\u00a0pavimento.', line='Um filme que o comprador entende sem ler uma planta.', note=FICTIONAL_TOWER),
             dict(layout='sheet', kicker='Pranchas técnicas',
                  sheets=dict(story=('03-corte-aa.svg', (0.278, 0.535), 1.17, 'Corte AA · 1:200'), feed=('02-planta-tipo.svg', (0.37, 0.505), 1.08, 'Planta do pavimento tipo · 1:100')),
                  head='As pranchas saem do mesmo modelo que as imagens.', line='Se um número muda no projeto, muda em tudo.', note=FICTIONAL_TOWER),
             dict(layout='seq', imgs=[('f030.jpg', 'Terreno'), ('f040.jpg', 'Fundação'), ('f080.jpg', 'Estrutura'), ('f141.jpg', 'Acabamento')], kicker='Etapas da obra',
                  head='Do terreno ao acabamento, etapa por etapa.', line='A mesma vista do começo ao fim, para o comprador acompanhar a obra.', note=FICTIONAL_TOWER),
         ]),
    dict(id='imovel-parado', title='Imóvel parado, alugado mais rápido', who='Imobiliárias',
         about='Para a imobiliária com imóveis vagos e anúncios fracos: a N6C cuida da vitrine e a corretagem continua com ela.',
         caption=('Tem imóvel parado na carteira? A N6C cuida da vitrine: trata as fotos, faz uma página para cada imóvel, deixa posts e anúncios prontos '
                  'e coloca um atendente no WhatsApp que responde e filtra os interessados a qualquer hora. A corretagem continua com a imobiliária. '
                  'Os valores eu te passo numa conversa rápida.'),
         pieces=[
             dict(layout='type', kicker='Para imobiliárias', head='Imóvel parado, alugado mais rápido.',
                  items=['Fotos tratadas, imagens 3D e planta\u00a0humanizada', 'Uma página por imóvel, pronta para\u00a0compartilhar', 'Posts e anúncios prontos para\u00a0publicar', 'Atendente no WhatsApp filtrando interessados a\u00a0qualquer\u00a0hora'],
                  line='A corretagem continua com a imobiliária. A gente cuida da vitrine.', note='Valores e prazos: fale com a gente.'),
             dict(layout='compare', imgs=[('planta-tecnica.png', 'Planta técnica'), ('planta-humanizada.png', 'Planta para o anúncio')], kicker='Planta humanizada',
                  head='Da planta técnica à planta que aluga.', line='Feita a partir da planta que você já tem, pronta para o anúncio.', note='Exemplo: apartamento de 2 dormitórios desenhado pela N6C.'),
             dict(layout='chat', kicker='Atendimento no WhatsApp', head='Responde e filtra os\u00a0interessados, até de\u00a0madrugada.',
                  line='Garantia, data de mudança, pet e visita: tudo perguntado antes de chegar ao corretor.',
                  chat=dict(name='Imobiliária · locação', sub='atendimento virtual', av='IM', msgs=[
                      ('in', 'Boa noite! O apê de 2 dormitórios ainda está para alugar?', '23:41'),
                      ('out', 'Boa noite! Aqui é o atendimento virtual da imobiliária. Está sim. Qual garantia você pretende usar, e para quando seria a mudança?', '23:41'),
                      ('in', 'Seguro-fiança. Queria mudar em dezembro.', '23:43'),
                      ('out', 'Anotado. Tem algum animal de estimação?', '23:43'),
                      ('in', 'Uma gata.', '23:44'),
                      ('out', 'O condomínio aceita. Posso marcar a visita para sábado às 10h? O corretor confirma com você amanhã cedo.', '23:44')]),
                  note='Conversa de exemplo.'),
         ]),
    dict(id='atendimento', title='Atendimento no WhatsApp', who='Quem vende pelo WhatsApp',
         about='Um atendimento virtual que responde na hora, por texto e por áudio, e passa para a equipe o que pede uma pessoa.',
         caption=('Sabe aquelas perguntas que chegam todo dia no WhatsApp, inclusive à noite? A N6C monta um atendimento virtual que responde na hora, '
                  'por texto ou por áudio, manda planta e ficha, e passa para a sua equipe, com um resumo, quando precisa de uma pessoa. '
                  'Ele se apresenta como atendimento virtual logo na primeira mensagem. Quer ver funcionando?'),
         pieces=[
             dict(layout='chat', kicker='Atendimento no WhatsApp', head='Resposta na hora, mesmo às 22h.',
                  line='As perguntas que se repetem, respondidas sem ninguém da equipe parar o que está fazendo.',
                  chat=dict(name='Vale do Araçá · vendas', sub='atendimento virtual', av='VA', msgs=[
                      ('in', 'Oi! O lote C02 ainda está disponível?', '22:07'),
                      ('out', 'Oi, aqui é o atendimento virtual do Vale do Araçá. Está sim: o C02 tem 375 m², 12,5 × 30 m, frente norte, na Rua das Aroeiras.', '22:07'),
                      ('in', 'E dá para parcelar?', '22:08'),
                      ('out', 'Tem parcelamento direto com a loteadora, com entrada. Quer que eu mande a ficha do lote com as condições?', '22:08'),
                      ('in', 'Quero!', '22:09'),
                      ('out-file', 'ficha-lote-C02.pdf|PDF · 2 páginas', '22:09')]),
                  note=FICTIONAL_LOTS),
             dict(layout='chat', kicker='Texto e áudio', head='Mandou áudio? Ele ouve e responde em áudio.',
                  line='Responde com voz natural e manda plantas, fichas e tabelas na mesma\u00a0conversa.',
                  chat=dict(name='Vale do Araçá · vendas', sub='atendimento virtual', av='VA', msgs=[
                      ('in-audio', '0:14', '19:32'),
                      ('out-audio', '0:21', '19:32'),
                      ('out-file', 'ficha-lote-C02.pdf|PDF · 2 páginas', '19:33'),
                      ('in', 'Perfeito. Dá para visitar no sábado?', '19:35'),
                      ('out', 'Dá sim. Vou passar para a equipe de vendas confirmar o horário com você.', '19:35')]),
                  note=FICTIONAL_LOTS),
             dict(layout='summary', kicker='Passagem para a equipe', head='Quando precisa de uma\u00a0pessoa, passa para a sua\u00a0equipe.',
                  line='Com o resumo da conversa, para ninguém perguntar tudo de novo.',
                  summary=dict(title='Resumo para a equipe de vendas', rows=[('Cliente', 'Mariana, pelo Instagram'), ('Interesse', 'Lote C02, 375 m², frente norte'),
                                                                               ('Pagamento', 'Entrada + parcelas direto com a loteadora'), ('Pedido', 'Visita no sábado de manhã'), ('Enviado', 'Ficha do lote C02 (PDF)')],
                               action='Confirmar o horário da visita'),
                  note='Exemplo, com dados do loteamento fictício Vale do Araçá.'),
         ]),
    dict(id='espelho', title='Espelho de vendas', who='Loteadoras e incorporadoras',
         about='O mapa de lotes que o comprador abre no celular, com situação, preço e WhatsApp em cada lote.',
         caption=('Olha esse espelho de vendas que a N6C faz: o comprador abre no celular, toca no lote e vê área, preço, situação e o botão de WhatsApp. '
                  'A situação de cada lote vem da planilha da equipe. O exemplo é um loteamento fictício e dá para abrir em n6c.org/demos/espelho-de-vendas. '
                  'Quer ver como ficaria o seu?'),
         pieces=[
             dict(layout='phone', img='espelho-mapa.png', kicker='Espelho de vendas', head='O comprador abre no celular e escolhe o lote.',
                  line='Disponíveis, reservados e vendidos, atualizados a partir da planilha da sua equipe.', note=FICTIONAL_LOTS),
             dict(layout='phone', img='espelho-lote.png', kicker='Ficha do lote', head='Área, preço, situação e WhatsApp em cada\u00a0lote.',
                  line='Ele toca no lote e já fala com quem vende.', note=FICTIONAL_LOTS),
             dict(layout='photo', img='maquete-topo.webp', pos='50% 40%', kicker='Maquete digital', head='A maquete do loteamento, a partir do seu desenho.',
                  line='Do DWG à imagem aérea, para o site, o folder e as redes.', note=FICTIONAL_LOTS),
         ]),
]
