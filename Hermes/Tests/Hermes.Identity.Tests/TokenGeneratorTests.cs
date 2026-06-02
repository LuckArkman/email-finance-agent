using System;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using Hermes.Domain.Identity;
using Hermes.Identity.Services;
using Microsoft.Extensions.Configuration;
using Xunit;

namespace Hermes.Identity.Tests;

public class TokenGeneratorTests
{
    [Fact]
    public void GenerateJwtToken_Should_Return_Valid_Token_With_Claims()
    {
        // Arrange
        var inMemorySettings = new System.Collections.Generic.Dictionary<string, string?> {
            {"Jwt:SecretKey", "test_secret_key_which_is_very_long_for_hmacsha256"},
            {"Jwt:Issuer", "TestIssuer"},
            {"Jwt:Audience", "TestAudience"}
        };

        IConfiguration configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(inMemorySettings)
            .Build();

        var generator = new TokenGenerator(configuration);
        var user = new User { Email = "test@example.com", UserRoles = new System.Collections.Generic.List<UserRole>() };

        // Act
        var tokenString = generator.GenerateJwtToken(user);

        // Assert
        Assert.False(string.IsNullOrEmpty(tokenString));
        var handler = new JwtSecurityTokenHandler();
        var jwtToken = handler.ReadJwtToken(tokenString);

        Assert.Equal("TestIssuer", jwtToken.Issuer);
        var emailClaim = jwtToken.Claims.First(c => c.Type == ClaimTypes.Email || c.Type == "email").Value;
        Assert.Equal("test@example.com", emailClaim);
    }
}
