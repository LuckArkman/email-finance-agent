namespace Hermes.Domain.Financial;

public enum InvoiceStatus
{
    Draft          = 0,   // Rascunho (pré-processamento)
    Pending        = 1,   // Em Aberto (dentro do prazo)
    Paid           = 2,   // Pago (comprovante associado)
    Overdue        = 3,   // Expirado (ultrapassou vencimento)
    Cancelled      = 4,   // Cancelado
    Reconciliation = 5,   // Em Conciliação (vencido, em renegociação)
    ReviewRequired = 6,   // Em Revisão (confiaça OCR baixa)
}
