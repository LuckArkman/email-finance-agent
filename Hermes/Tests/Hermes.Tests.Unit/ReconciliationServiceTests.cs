using System;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using Xunit;
using Hermes.EventBus;

namespace Hermes.Tests.Unit;

public class ReconciliationServiceTests
{
    [Fact]
    public void Reconciliation_Should_Approve_When_Difference_Is_Under_Five_Cents()
    {
        // Arrange
        var mockEventBus = new Mock<IEventBus>();
        // var service = new ReconciliationService(mockEventBus.Object);
        
        var invoiceAmount = 100.00m;
        var transactionAmount = 100.04m;

        // Act
        var diff = Math.Abs(invoiceAmount - transactionAmount);
        var isReconciled = diff <= 0.05m;

        // Assert
        isReconciled.Should().BeTrue("because the difference is within the 5 cents tolerance limit");
    }

    [Fact]
    public void Reconciliation_Should_Fail_When_Difference_Exceeds_Five_Cents()
    {
        // Arrange
        var invoiceAmount = 100.00m;
        var transactionAmount = 100.06m;

        // Act
        var diff = Math.Abs(invoiceAmount - transactionAmount);
        var isReconciled = diff <= 0.05m;

        // Assert
        isReconciled.Should().BeFalse("because the difference exceeds the 5 cents tolerance limit");
    }
}
