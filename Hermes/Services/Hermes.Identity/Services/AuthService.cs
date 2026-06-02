using System.Collections.Generic;
using Hermes.Domain.Identity;

namespace Hermes.Identity.Services;

public class AuthService
{
    private readonly TokenGenerator _tokenGenerator;
    
    // Simulating a DB context with an in-memory list for demo/tests
    private readonly List<User> _users = new();

    public AuthService(TokenGenerator tokenGenerator)
    {
        _tokenGenerator = tokenGenerator;
    }

    public User Register(string email, string password, string firstName)
    {
        var hash = BCrypt.Net.BCrypt.HashPassword(password);
        var user = new User
        {
            Email = email,
            PasswordHash = hash,
            FirstName = firstName
        };
        _users.Add(user);
        return user;
    }

    public string Login(string email, string password)
    {
        var user = _users.Find(u => u.Email == email);
        if (user == null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
        {
            throw new System.UnauthorizedAccessException("Invalid credentials");
        }

        return _tokenGenerator.GenerateJwtToken(user);
    }
}
