using System;
using System.Threading.Tasks;
using Hermes.Domain.Identity;
using Hermes.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace Hermes.Identity.Services;

public class AuthService
{
    private readonly TokenGenerator _tokenGenerator;
    private readonly HermesDbContext _db;

    public AuthService(TokenGenerator tokenGenerator, HermesDbContext db)
    {
        _tokenGenerator = tokenGenerator;
        _db = db;
    }

    public User Register(string email, string password, string firstName)
    {
        // Check if user already exists
        var existing = _db.Users.FirstOrDefault(u => u.Email == email);
        if (existing != null)
            throw new InvalidOperationException("User already exists.");

        var hash = BCrypt.Net.BCrypt.HashPassword(password);
        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = email,
            PasswordHash = hash,
            FirstName = firstName,
            CreatedAt = DateTime.UtcNow
        };
        _db.Users.Add(user);
        _db.SaveChanges();
        return user;
    }

    public string Login(string email, string password)
    {
        var user = _db.Users.FirstOrDefault(u => u.Email == email);
        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
        {
            throw new UnauthorizedAccessException("Invalid credentials");
        }

        return _tokenGenerator.GenerateJwtToken(user);
    }
}
