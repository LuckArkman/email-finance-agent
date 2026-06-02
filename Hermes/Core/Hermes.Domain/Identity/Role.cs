using System.Collections.Generic;
using Hermes.Domain.Common;

namespace Hermes.Domain.Identity;

public class Role : BaseEntity
{
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    public ICollection<RolePermission> Permissions { get; set; } = new List<RolePermission>();
}
