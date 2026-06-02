using System;
using System.Collections.Generic;
using System.Linq;
using Hermes.Domain.Identity;

namespace Hermes.Identity.Services;

public class RoleManager
{
    private readonly List<Role> _roles = new();

    public Role CreateRole(string name, string description, List<string> permissions)
    {
        var role = new Role
        {
            Name = name,
            Description = description,
            Permissions = permissions.Select(p => new RolePermission { Permission = p }).ToList()
        };
        _roles.Add(role);
        return role;
    }

    public void AssignRoleToUser(User user, Role role)
    {
        var userRole = new UserRole
        {
            UserId = user.Id,
            User = user,
            RoleId = role.Id,
            Role = role
        };
        user.UserRoles ??= new List<UserRole>();
        user.UserRoles.Add(userRole);
    }
}
