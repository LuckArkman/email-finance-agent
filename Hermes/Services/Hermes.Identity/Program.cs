using Hermes.Domain.Identity;
using Hermes.Identity.Services;
using Hermes.Infrastructure.Extensions;
using Hermes.Infrastructure.Data;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;
using System.IO;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo(@"/shared/keys"))
    .SetApplicationName("Hermes.EcoSystem");

// Register PostgreSQL database (HermesDbContext)
builder.Services.AddHermesDatabase(builder.Configuration);

// Configurar geração e validação de tokens JWT
builder.Services.AddSingleton<TokenGenerator>();
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<RoleManager>();

// Políticas Globais de Cookies (Anti-CSRF, HTTPS-Only)
builder.Services.Configure<CookiePolicyOptions>(options =>
{
    options.MinimumSameSitePolicy = SameSiteMode.Strict;
    options.HttpOnly = Microsoft.AspNetCore.CookiePolicy.HttpOnlyPolicy.Always;
    options.Secure = CookieSecurePolicy.Always;
});

builder.Services.AddAuthorizationBuilder()
    .AddPolicy(SystemPermissions.InvoicesRead, policy => policy.RequireClaim("Permission", SystemPermissions.InvoicesRead))
    .AddPolicy(SystemPermissions.InvoicesWrite, policy => policy.RequireClaim("Permission", SystemPermissions.InvoicesWrite))
    .AddPolicy(SystemPermissions.UsersRead, policy => policy.RequireClaim("Permission", SystemPermissions.UsersRead))
    .AddPolicy(SystemPermissions.UsersWrite, policy => policy.RequireClaim("Permission", SystemPermissions.UsersWrite))
    .AddPolicy(SystemPermissions.RolesManage, policy => policy.RequireClaim("Permission", SystemPermissions.RolesManage));

var app = builder.Build();

// Auto-migrate database on startup
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<HermesDbContext>();
    db.Database.Migrate();
}

app.UseCookiePolicy();

app.UseAuthorization();

var authGroup = app.MapGroup("/api/hermes/auth");

authGroup.MapPost("/register", (AuthService authService, RegisterRequest request) =>
{
    var user = authService.Register(request.Email, request.Password, request.FirstName);
    return Results.Ok(new { user.Id, user.Email, user.FirstName });
});

authGroup.MapPost("/login", (AuthService authService, LoginRequest request) =>
{
    try
    {
        var token = authService.Login(request.Email, request.Password);
        return Results.Ok(new { Token = token });
    }
    catch (System.UnauthorizedAccessException)
    {
        return Results.Unauthorized();
    }
});

var rolesGroup = app.MapGroup("/api/hermes/auth/roles").RequireAuthorization(SystemPermissions.RolesManage);

rolesGroup.MapPost("/", (RoleManager roleManager, CreateRoleRequest request) =>
{
    var role = roleManager.CreateRole(request.Name, request.Description, request.Permissions);
    return Results.Ok(role);
});

rolesGroup.MapPost("/assign", (RoleManager roleManager, AssignRoleRequest request) =>
{
    // Mock user for now. In a real app, you'd fetch the user and role from DB.
    var user = new User { Email = request.Email };
    var role = new Role { Name = "DynamicRole" };
    // ID mock workaround ignored for now
    roleManager.AssignRoleToUser(user, role);
    return Results.Ok();
});

app.MapGet("/health", () => Results.Ok(new { Status = "Healthy" }));

app.Run();

public record RegisterRequest(string Email, string Password, string FirstName);
public record LoginRequest(string Email, string Password);
public record CreateRoleRequest(string Name, string Description, System.Collections.Generic.List<string> Permissions);
public record AssignRoleRequest(string Email, System.Guid RoleId);
