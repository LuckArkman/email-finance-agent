using System;
using System.Collections.Generic;
using System.Linq;
using Hermes.Domain.Identity;
using Hermes.Identity.Services;
using Xunit;

namespace Hermes.Identity.Tests;

public class RoleManagerTests
{
    [Fact]
    public void CreateRole_Should_Initialize_With_Permissions()
    {
        var manager = new RoleManager();
        
        var role = manager.CreateRole("Admin", "Administrator", new List<string> { SystemPermissions.InvoicesRead, SystemPermissions.InvoicesWrite });

        Assert.Equal("Admin", role.Name);
        Assert.Equal(2, role.Permissions.Count);
        Assert.Contains(role.Permissions, p => p.Permission == SystemPermissions.InvoicesWrite);
    }

    [Fact]
    public void AssignRoleToUser_Should_Add_Role_To_UserRoles()
    {
        var manager = new RoleManager();
        var role = manager.CreateRole("User", "Basic User", new List<string> { SystemPermissions.InvoicesRead });
        var user = new User { Email = "test@example.com" };

        manager.AssignRoleToUser(user, role);

        Assert.Single(user.UserRoles);
        Assert.Equal(role.Id, user.UserRoles.First().RoleId);
    }
}
