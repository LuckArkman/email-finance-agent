using System;
using Hermes.Domain.Common;

namespace Hermes.Domain.Identity;

public class RolePermission : BaseEntity
{
    public Guid RoleId { get; set; }
    public Role Role { get; set; } = null!;
    
    public string Permission { get; set; } = string.Empty; // Using SystemPermissions constants
}
