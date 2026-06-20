select
    id_cliente,
    nome,
    cpf,
    email,
    telefone,
    status_cliente,
    uf
from {{ source('raw', 'clientes') }}