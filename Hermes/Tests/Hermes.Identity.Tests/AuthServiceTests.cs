using System;
using Hermes.Identity.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
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
        
        var options = new Microsoft.EntityFrameworkCore.DbContextOptionsBuilder<Hermes.Infrastructure.Data.HermesDbContext>()
            .UseInMemoryDatabase(databaseName: "Test_Db")
            .Options;
        var mockTenantProvider = new Moq.Mock<Hermes.Domain.Tenancy.ITenantProvider>();
        mockTenantProvider.Setup(m => m.GetCurrentTenant()).Returns(new Hermes.Domain.Tenancy.TenantContext { TenantId = Guid.NewGuid() });
        var dbContext = new Hermes.Infrastructure.Data.HermesDbContext(options, mockTenantProvider.Object);
        
        _authService = new AuthService(tokenGenerator, dbContext);
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
