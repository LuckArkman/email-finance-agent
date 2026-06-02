using System;
using Hermes.Identity.Services;
using Microsoft.Extensions.Configuration;
using Xunit;

namespace Hermes.Identity.Tests;

public class AuthServiceTests
{
    private readonly AuthService _authService;

    public AuthServiceTests()
    {
        var inMemorySettings = new System.Collections.Generic.Dictionary<string, string?> {
            {"Jwt:SecretKey", "test_secret_key_which_is_very_long_for_hmacsha256"}
        };
        IConfiguration config = new ConfigurationBuilder().AddInMemoryCollection(inMemorySettings).Build();
        var tokenGenerator = new TokenGenerator(config);
        _authService = new AuthService(tokenGenerator);
    }

    [Fact]
    public void Register_Should_Hash_Password()
    {
        // Act
        var user = _authService.Register("test@test.com", "password123", "John");

        // Assert
        Assert.NotNull(user);
        Assert.NotEqual("password123", user.PasswordHash);
        Assert.True(BCrypt.Net.BCrypt.Verify("password123", user.PasswordHash));
    }

    [Fact]
    public void Login_Should_Return_JWT_When_Valid()
    {
        // Arrange
        _authService.Register("login@test.com", "mypass", "Jane");

        // Act
        var token = _authService.Login("login@test.com", "mypass");

        // Assert
        Assert.NotNull(token);
        Assert.True(token.Length > 0);
    }

    [Fact]
    public void Login_Should_Throw_When_Invalid()
    {
        // Act & Assert
        Assert.Throws<UnauthorizedAccessException>(() => _authService.Login("invalid@test.com", "wrongpass"));
    }
}
