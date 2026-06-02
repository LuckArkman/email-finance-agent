using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Gateway.Extensions;

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddGatewayServices(this IServiceCollection services)
    {
        // Place core dependencies, YARP configuration or custom services here.
        return services;
    }
}
